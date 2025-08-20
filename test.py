import requests

# Define the URL for the UCSC Table Browser
url = "https://genome.ucsc.edu/cgi-bin/hgTables"

# Set up the POST data parameters
data = {
    "clade": "vertebrate",
    "org": "Zebrafish",
    "db": "danRer11",
    "hgta_group": "genes",
    "hgta_track": "refSeqComposite",
    "hgta_table": "ncbiRefSeq",
    "hgta_regionType": "genome",
    "position": "",
    "hgta_outputType": "primaryTable",
    "hgta_outFileName": "",  # Leave empty to get the output inline
    "boolshad.doNotRedirect": "1",  # Prevent redirection
    "hgta_doTopSubmit": "get output"  # Trigger the data retrieval
}

# Make the POST request
response = requests.post(url, data=data)

# Check if the response is successful
if response.status_code == 200 and b'HGERROR-START' not in response.content:
    # Save the content to a file
    with open("ucsc_refseq.tsv", "wb") as f:
        f.write(response.content)
    print("✅ Data downloaded successfully as ucsc_refseq.tsv")
else:
    print("❌ Failed to retrieve data. Please check the parameters and try again.")
