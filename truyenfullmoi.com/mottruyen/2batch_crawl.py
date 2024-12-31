import subprocess
def crawl_data():
    file_path = "dao-tinh_132.txt"
    with open(file_path, "r") as file:
        links = file.read().strip().splitlines()
    
    for link in links:
        try:
            subprocess.run(
                ["bash", "crawl_truyen.sh", link],
                check=True
            )
        except subprocess.CalledProcessError as e:
            with open("error.log", "a") as error_file:
                error_file.write(f"Error crawling link '{link}': {e}\n")

if __name__ == "__main__":
    crawl_data()
    print("Done!")