from prefect import flow,task

@task(name="say-hello")
def say_hello(name: str="World") -> str:
    greeting = f"Hello, {name}!"
    print(greeting)
    return greeting

@flow(name="hello-world-flow",log_prints=True)
def simple_hello_world_task(name : str="World") -> str:
    print("start")
    results = say_hello(name)
    print("end")
    return results

if __name__ == "__main__":
    res=simple_hello_world_task()
    print(res)