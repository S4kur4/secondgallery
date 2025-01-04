#!/bin/bash

# Function to hash password using SHA256
hash_password() {
    local password=$1
    echo -n "${password}" | sha256sum | awk '{print $1}'
}

# Function to update environment variable in .env file
update_env_var() {
    local key=$1
    local value=$2
    local file=".env"

    # Create temp file
    touch "$file.tmp"

    if [ -f "$file" ]; then
        while IFS= read -r line || [ -n "$line" ]; do
            if [[ $line =~ ^$key= ]]; then
                echo "$key=$value" >> "$file.tmp"
            else
                echo "$line" >> "$file.tmp"
            fi
        done < "$file"
    fi

    # If key doesn't exist in file, append it
    if ! grep -q "^$key=" "$file"; then
        echo "$key=$value" >> "$file.tmp"
    fi

    # Replace original file
    mv "$file.tmp" "$file"
}

# Function to check if credentials already exist
check_existing_credentials() {
    if [ -f .env ]; then
        username=$(grep "^ADMIN_USERNAME=" .env | cut -d'=' -f2)
        password=$(grep "^ADMIN_PASSWORD=" .env | cut -d'=' -f2)

        if [ ! -z "$username" ] && [ ! -z "$password" ]; then
            echo "Admin credentials already exist."
            read -p "Do you want to create new credentials? (y/N): " response
            if [[ ! $response =~ ^[Yy]$ ]]; then
                echo "Operation cancelled."
                exit 0
            fi
        fi
    fi
}

# Main script
echo "This script will help you initialize the password for the admin account used to manage the photos in Secondgallery."

# Check existing credentials
check_existing_credentials

# Get username
while true; do
    read -p "Enter admin username: " username
    if [ ! -z "$username" ]; then
        break
    else
        echo "Username cannot be empty. Please try again."
    fi
done

# Get password
while true; do
    read -s -p "Enter admin password: " password
    echo
    read -s -p "Confirm admin password: " password_confirm
    echo

    if [ -z "$password" ]; then
        echo "Password cannot be empty. Please try again."
        continue
    fi

    if [ "$password" != "$password_confirm" ]; then
        echo "Passwords do not match. Please try again."
        continue
    fi

    break
done

# Hash password
hashed_password=$(hash_password "$password")

# Update credentials in .env file
update_env_var "ADMIN_USERNAME" "$username"
update_env_var "ADMIN_PASSWORD" "$hashed_password"

echo "Admin credentials have been successfully created."
