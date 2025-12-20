# Skeleton:

# Present a home screen that tells who its made by and askes for a url or IP address to scan

# Take the input and verify that its a valid IP or if they entered in a URL verify and give back the IP --- maybe ping it to make sure we are able to connect to the host ??? (it would also be cool to see the steps when running)
    # if the user types in a url convert that url into and ip address
        # Assign target to the IP

# Scan the ports for that IP using multi-treading so its fast

# Present what ports are open to the user 

# Ask the user if they want to return to the home screen to allow them to run the program again or if they want to exit. 


# ----- CODE -----


import socket
import threading
import queue
import sys


# Prints a home screen 
def homeScreen():
    print("\n" + "=" * 50)
    print("\n Welcome, this tool is a port scanner built in Python. It will eventually also tell you the service and version running on the open ports.")
    print("\n" + "=" * 50 + "\n")


# Gets the target from the user
def getTarget():
    target = input("Enter a URL or IP address to scan: ").strip()

    try:
        ip = socket.gethostbyname(target) # Checks by URL and IP
        print(f"[+] Target resolved to IP: {ip}")
        return ip
    
    # Unless there is a address error
    except socket.gaierror:
        print("[-] Invalid URL or IP address")
        return None
    

# Checks if host is reachable 
def checkHost(ip):
    try:
        socket.setdefaulttimeout(1)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # sets up a tcp internet connection
        s.settimeout(2)
        s.connect((ip, 80))
        s.close()

        print("[+] Host is reachable")
        return True
    
    except socket.timeout:
        print("[-] Connection timed out")

    except ConnectionRefusedError:
        print("[-] Host reachable but port 80 is closed")
        return True
    
    except OSError:
        print("[-] Network unreachable")
        return False
    

# Asks user for a range of ports to scan
def getPortRange():
    while True:
        user_input = input("\nEnter port range (e.g. 20-8080): ").strip()

        try:
            # Split on dash
            startStr, endStr = user_input.split("-")

            # Convert to int
            startPort = int(startStr)
            endPort = int(endStr)

            # Validate range
            if 1 <= startPort <= 65535 and 1 <= endPort <=65535:
                if startPort <= endPort:
                    return startPort, endPort
            
            print("[-] Port range must be between 1 and 65535 and the starting port must be less than or equal to the ending port")

        except ValueError:
            # Raised if split or int conversion fails
            print("[-] Invalid format. Use: start-end (example: 20-8080)")

# Scans a port
def scanPort(ip, port):
    try:
        # Creates a TCP Socket (IPv4 + TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Sets a timeout 
        s.settimeout(0.5)

        # connect_ex returns a 0 if the connection is successful
        result = s.connect_ex((ip, port))

        # Close connection
        s.close()

        if result == 0:
            print(f"[OPEN] Port {port}")

    except OSError:
        #ignore network errors
        pass


# Single thread worker
def worker(ip, portQueue):
    # Each thread runs this function, it pulls ports from the queue and scans them
    while not portQueue.empty():
        port = portQueue.get()
        scanPort(ip, port)
        portQueue.task_done()


# Thread controller
def scanPorts(ip, startPort, endPort):
    portQueue = queue.Queue()

    # Add all ports to the queue
    for port in range(startPort, endPort + 1):
        portQueue.put(port)

    # Number of threads
    threadCount = 100

    # Start worker threads
    for _ in range(threadCount):
        t = threading.Thread(target=worker, args=(ip, portQueue))
        t.daemon = True
        t.start()

    # Wait until all ports are scanned
    portQueue.join()

def runScanner(ip):
    startPort, endPort = getPortRange()

    print(f"\n [+] Scanning Ports {startPort} to {endPort} on {ip}\n")

    scanPorts(ip, startPort, endPort)

    print("\n[+] Scan Complete")

def main():
    while True:
        # Show home screen
        homeScreen()

        # Ask for a target
        ip = getTarget()

        # If target is invalid restart loop
        if ip is None:
            continue

        # Check if the host is reachable
        #if not checkHost(ip):
        #    print("[-] Skipping Scan")
        #    continue

        # Ask for port range
        startPort, endPort = getPortRange()

        print(f"\n[+] Starting scan on {ip}")
        print(f"[+] Ports {startPort} to {endPort}\n")

        # Multithreaded port scan
        scanPorts(ip, startPort, endPort)

        # Ask user if they want to run another scan
        choice = input("\n Scan another target? (y/n) ").strip().lower()

        if choice != "y":
            print("Exiting")
            break



if __name__ == "__main__":
    main()


