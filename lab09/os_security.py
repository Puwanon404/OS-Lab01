
# os_security.py

import os
import stat


def main():
    secure_file = "secret_config.json"

    # Remove an old test file if it exists
    if os.path.exists(secure_file):
        os.chmod(secure_file, 0o666)
        os.remove(secure_file)

    # Create a new file
    with open(secure_file, "w") as f:
        f.write("{'api_key': '12345XYZ'}")

    print(f"Created {secure_file}.")

    # Set the file to read-only for the owner
    print("Locking file permissions to Read-Only (0o400)...")
    os.chmod(secure_file, 0o400)

    print(
        f"New Permissions: "
        f"{stat.filemode(os.stat(secure_file).st_mode)}"
    )

    # Try to write to the read-only file
    print("\nAttempting to overwrite the file...")

    try:
        with open(secure_file, "a") as f:
            f.write("\nMALICIOUS HACKER DATA")
        print("Success! Data written.")
    except PermissionError as e:
        print(f">>> [OS KERNEL BLOCKED] PermissionError: {e}")
        print(">>> The Operating System successfully protected the file!")


if __name__ == "__main__":
    main()