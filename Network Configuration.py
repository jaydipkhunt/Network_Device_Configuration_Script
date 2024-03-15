import paramiko
import time

# Function to remove ANSI escape codes from the output
def remove_escape_codes(output):
    import re
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)

# Define SSH connection parameters
USERNAME = 'Enter Your Username'
PASSWORD = 'Enter Your Password'
PORT = 22

# Input and output file paths
input_file_path = 'input_hosts.txt'  # Path to input file containing hostnames
commands_file_path = 'commands.txt'   # Path to input file containing configuration commands
output_file_path = 'output_data.txt'  # Path to output file to store data

# Read configuration commands from the commands file
with open(commands_file_path, 'r') as commands_file:
    configuration_commands = commands_file.readlines()

# Initialize SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Open the input file to read hostnames
    with open(input_file_path, 'r') as input_file:
        hostnames = input_file.readlines()

    # Open the output file to write data
    with open(output_file_path, 'w') as output_file:
        for hostname in hostnames:
            hostname = hostname.strip()  # Remove leading/trailing whitespaces and newlines

            try:
                # Connect to the switch
                ssh_client.connect(hostname, port=PORT, username=USERNAME, password=PASSWORD, timeout=10)

                # Create an interactive shell
                shell = ssh_client.invoke_shell()

                # Send configuration commands to the switch
                for command in configuration_commands:
                    shell.send(command.strip() + '\n')
                    time.sleep(1)  # Adjust sleep time as needed

                # Wait for the commands to execute and the output to be generated
                time.sleep(2)  # Adjust sleep time as needed

                # Read the output and remove ANSI escape codes
                output = shell.recv(65535).decode()
                output = remove_escape_codes(output)

                # Write the output to the output file
                output_file.write(f"Output for {hostname}:\n")
                output_file.write(output)
                output_file.write('\n\n')

                print(f"Configuration pushed to {hostname} successfully.")

            except paramiko.AuthenticationException:
                print(f"Authentication failed for {hostname}, please verify your credentials.")
            except paramiko.SSHException as ssh_err:
                print(f"Unable to establish SSH connection to {hostname}: {ssh_err}")
            except Exception as e:
                print(f"An error occurred for {hostname}: {e}")

finally:
    # Close the SSH client
    ssh_client.close()
