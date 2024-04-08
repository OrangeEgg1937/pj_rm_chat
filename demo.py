import subprocess

if __name__ == "__main__":
    try:
        with subprocess.run(["python", "connection/host.py",
                             "-ip", "localhost",
                             "-name", "Host",
                             "-port", "32800"],
                            check=True) as process:
            print("Host is started")
            while True:
                print("waiting for the connection...")
    except Exception as e:
        print(f"Error: {e}")
        print("Please see the error message above.")

    print("end of the script")
