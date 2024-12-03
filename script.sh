#!/bin/bash
python scraper.py
sed -i 's/^https\?:\/\///' out.txt
sed -i 's/\/.*//' out.txt
if ! command -v emailfinder &>/dev/null; then
  echo "Error: emailfinder command not found. Please make sure it's installed and in your PATH."
  exit 1
fi
input_file="out.txt"
echo "Checking domains for emails..."
if [ ! -f "$input_file" ]; then
  echo "Error: $input_file not found."
  exit 1
fi
while IFS= read -r domain || [[ -n "$domain" ]]; do
  if [[ -n "$domain" && ! "$domain" =~ ^#.* ]]; then
    emailfinder -d "$domain" | grep '@' | grep -v 'Josue'
  fi
done < "$input_file" > emails.txt
rm -r out.txt
echo "Check emails.txt for the list of scraped emails."