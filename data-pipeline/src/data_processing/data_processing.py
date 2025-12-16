"""
Data Processing Pipeline
Download data from S3, clean it, transform it, and upload results back to S3.
"""

import os
import boto3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import tempfile

def process_ecommerce_data():
    """Download, process, and upload e-commerce data"""
    
    print("Starting data processing...")
    
    # Load environment variables
    load_dotenv()
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    region = os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-3')
    
    if not bucket_name:
        print("ERROR: AWS_S3_BUCKET_NAME not found in .env file!")
        return False
    
    print(f"Processing data from bucket: {bucket_name}")
    
    try:
        # Create S3 client
        s3 = boto3.client('s3',region_name=region)
        
        # Step 1: Download data from S3
        print("\nStep 1: Downloading data from S3...")
        datasets = download_data_from_s3(s3, bucket_name)
        
        # Step 2: Clean and transform data
        print("\nStep 2: Cleaning and transforming data...")
        processed_datasets = transform_data(datasets)
        
        # Step 3: Create business metrics
        print("\nStep 3: Creating business metrics...")
        business_metrics = create_business_metrics(processed_datasets)
        
        # Step 4: Upload processed data back to S3
        print("\nStep 4: Uploading processed data to S3...")
        upload_success = upload_processed_data(s3, bucket_name, processed_datasets, business_metrics)
        
        if upload_success:
            print("\nSUCCESS: Data processing pipeline completed!")
            return True
        else:
            print("\nERROR: Failed to upload processed data")
            return False
            
    except Exception as e:
        print(f"ERROR: Data processing failed: {e}")
        return False
    
def download_data_from_s3(s3,bucket_name):

    datasets ={}
    data_files = ['customers.csv','products.csv','orders.csv','order_items.csv','reviews.csv']
    for file_name in data_files:
        try:
            print(f"downloading {file_name}...")
            s3_key = f"raw-data/{file_name}"
            local_path = os.path.join(tempfile.gettempdir(),file_name)
            s3.download_file(bucket_name,s3_key,local_path)
            df=pd.read_csv(local_path)
            dataset_name=file_name.replace(".csv","")
            datasets[dataset_name]=df

            print(f'Loaded {dataset_name} : {len(df)} records')
            os.remove(local_path)
        except Exception as e:
            print(f"failed to download {file_name} : {e}")
    return datasets
def transform_data(datasets):
    processed ={}
    
    # process customer data
    if 'customers' in datasets:
        customers = datasets['customers'].copy()

        # clean email adresses
        customers['email'] = customers['email'].str.lower().str.strip()
        
        # convert dates
        customers['date_of_birth'] = pd.to_datetime(customers['date_of_birth'])
        customers['registration_date'] = pd.to_datetime(customers['registration_date'])

        #calculate age
        customers['age'] = (datetime.now()-customers['date_of_birth']).dt.days //365

        #create age groups
        customers['age_group'] =pd.cut(customers['age'],bins=[0,25,35,50,65,100],
                                labels=['18-25','26-35','36-50','51-65','65+'])
        processed['customer_clean']= customers
        print(f"processed customers:{len(customers)} records")
    #process products data
    if 'products' in datasets:
        products= datasets['products'].copy()

        # clean product name
        products['product_name'] = products['product_name'].str.strip()
        
        # convert prices to numeric
        products['price'] = pd.to_numeric(products['price'],errors ='coerce')


        #create price groups
        products['price_category'] =pd.cut(products['price'],bins=[0,50,150,500, float('inf')],
                                labels=['Budget','Mid-range','Premium','Luxury'])
        processed['products_clean']= products
        print(f"processed products:{len(products)} records")
    #process orders data
    if 'orders' in datasets:
        orders = datasets['orders'].copy()
        #convert date
        orders['order_date']=pd.to_datetime(orders['order_date'])

        #convert total amount to numeric
        orders['total_amount'] = pd.to_numeric(orders['total_amount'],errors='coerce')

        #extract month and year for seasonal analysis
        orders['order_month'] = orders['order_date'].dt.month
        orders['order_year'] = orders['order_date'].dt.year

        processed['orders_clean']=orders

        print(f"Processed orders: {len(orders)} records")

    #process order_item data
    if 'order_items' in datasets:
        order_items=datasets['order_items'].copy()
        
        order_items['quantity'] = pd.to_numeric(order_items['quantity'],errors='coerce')
        order_items['unit_price'] = pd.to_numeric(order_items['unit_price'],errors='coerce')

        order_items['total_price'] = order_items['quantity']*order_items['unit_price']
        processed['order_items_clean'] =order_items

        print(f"processed order_items: {len(order_items)} records")   

    #process review data    
    if 'reviews' in datasets:
        reviews = datasets['reviews'].copy()
        #concert date
        reviews['review_date']=pd.to_datetime(reviews['review_date'])

        #convert to num
        reviews['rating']=pd.to_numeric(reviews['rating'],errors='coerce')

        #create rating categories
        reviews['rating_category']=reviews['rating'].apply(
            lambda x:'Excellent' if x>=4.5 else 
                        'Good' if x>=3.5 else
                        'Average' if x>=2.5 else 'Poor'
        )
        processed['reviews_clean']=reviews
        print(f"processed revies: {len(reviews)} records")
    return processed
def create_business_metrics(processed_datasets):
    metrics={}
    #customer metrics
    if 'customers_clean' in processed_datasets and 'orders_clean' in processed_datasets:
        customers = processed_datasets['customers_clean']
        orders=processed_datasets['orders_clean']

        #customer lifetime value
        customer_metrics=orders.groupby('customer_id').agg({
            'total_amount':['sum','count','mean'],
            'order_date':['min','max']
        }).round(2)
        customer_metrics.columns=['total_spent','order_count','average_order_value','first_order','last_order']
        customer_metrics=customer_metrics.reset_index()

        #merge with customer data
        customer_metrics=customer_metrics.merge(customers[{'customers_id','age_group'}])

        metrics['customer_metrics']=customer_metrics
        print(f'Created customer metrics: {len(customer_metrics)} customers')

    #product metrics
    if 'products_clean' in processed_datasets and 'order_items_clean' in processed_datasets:
        products=processed_datasets['products_clean']
        order_items=processed_datasets['order_items_clean']

        #product sales metrics
        product_metrics=order_items.groupby('product_id').agg({
            'quantity':'sum',
            'total_price':'sum',
            'order_id':'count'
        }).round(2)

        product_metrics.columns=['total_quantity_sold','total_revenue','number_of_orders']
        product_metrics=product_metrics.reset_index()

        #merge with product data
        product_metrics=product_metrics.merge(products[['product_id','product_name','category','price']],on='product_id')

        metrics['product_metrics']=product_metrics
        print(f'Created product metrics:{len(product_metrics)} products')
    
    if 'orders_clean' in processed_datasets:
        orders = processed_datasets['orders_clean']
        
        monthly_sales = orders.groupby(['order_year', 'order_month']).agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).round(2)
        
        monthly_sales.columns = ['total_revenue', 'order_count']
        monthly_sales = monthly_sales.reset_index()
        
        metrics['monthly_sales'] = monthly_sales
        print(f"Created monthly sales trends: {len(monthly_sales)} months")
    
    return metrics
def upload_processed_data(s3,bucket_name,processed,metrics):

    upload_count = 0
    total_files = len(processed) + len(metrics)

    # Upload processed datasets
    for dataset_name, df in processed.items():
        try:
            # Save a temporary csv file
            local_path = os.path.join(tempfile.gettempdir(), f"{dataset_name}.csv")
            df.to_csv(local_path, index=False)

            # Upload to S3
            s3_key = f"processed/{dataset_name}.csv"
            s3.upload_file(local_path,bucket_name,s3_key)

            print(f"Uploaded {dataset_name}: {len(df)} records")
            upload_count += 1

            # Clean up
            os.remove(local_path)

        except Exception as e:
            print(f"Failed to upload {dataset_name}: {e}")

        # Upload business metrics
    for metric_name, df in metrics.items():
        try:
            # Save a temporary csv file
            local_path = os.path.join(tempfile.gettempdir(), f"{metric_name}.csv")
            df.to_csv(local_path, index=False)

            # Upload to S3
            s3_key = f"processed/metrics/{metric_name}.csv"
            s3.upload_file(local_path,bucket_name,s3_key)

            print(f"Uploaded {metric_name}: {len(df)} records")
            upload_count += 1

            # Clean up
            os.remove(local_path)

        except Exception as e:
            print(f"Failed to upload {metric_name}: {e}")

    return upload_count == total_files

if __name__ == "__main__":
    success = process_ecommerce_data()
    if success:
        print("\n Next step : orchestration with prefect")
    else:
        print("\nfix the error and try again")
    
