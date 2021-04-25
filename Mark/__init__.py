import logging
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import uuid
import requests
import fitz
import io
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    #name = req.params.get('name')
    #parse POST bosy to json
    req_body = req.get_json()
    inputPDF = req_body.get('InputPDF_URL')

    #Get azure blob connection string. To learn how to use local stored keys check https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    greenWords = ["exceeding expectations"," positive ", " favourable ", " profit up", " excellent ", " transformational "]
    redWords = [" challenging ", " difficult ", " unpredictable ", " lower ", " poor ", " tough ", "below expectations", " brexit "]
    numberOfGreenwords = 0
    numberOfRedwords = 0
    azure_blob_container_name = "markedreports"

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    #generate unique file name
    file_name = uuid.uuid4().hex + ".pdf"

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=azure_blob_container_name, blob=file_name)
    
    # open the pdf file
    #r = requests.get("https://pdfhelperstorage.blob.core.windows.net/markedreports/Smurfit_Kappa_Annual_Report_2020.pdf")
    r = requests.get(inputPDF)
    inmemoryfile = io.BytesIO(r.content)
    #PDFObject = PyPDF2.PdfFileReader(inmemoryfile)
    doc = fitz.open(stream=inmemoryfile, filetype="pdf")

    # get number of pages
    NumPages = doc.page_count

    # loop all pages
    for i in range(0, NumPages):
        page = doc[i]
        #text = "positive"
        #text_instances = page.searchFor(text)
        
        
        # loop all green words
        for gword in greenWords:
            text_instances = page.searchFor(gword)
            numberOfGreenwords = numberOfGreenwords + len(text_instances)

            #HIGHLIGHT green words
            for inst in text_instances:
                highlight = page.addHighlightAnnot(inst)
                highlight.setColors({"stroke":(0, 1, 0), "fill":(0.75, 0.8, 0.95)})
                highlight.update()
        
        # loop all red words
        for rword in redWords:
            text_instances = page.searchFor(rword)
            numberOfRedwords = numberOfRedwords + len(text_instances)

            #HIGHLIGHT red words
            for inst in text_instances:
                highlight = page.addHighlightAnnot(inst)
                highlight.setColors({"stroke":(1, 0, 0), "fill":(0.75, 0.8, 0.95)})
                highlight.update()

    # upload output file to blob
    blob_client.upload_blob(doc.tobytes())

    #return func.HttpResponse(f"https://{blob_client.account_name}.blob.core.windows.net/{azure_blob_container_name}/{file_name}")
    marked_pdf = f"https://{blob_client.account_name}.blob.core.windows.net/{azure_blob_container_name}/{file_name}"
    resultJSON = {"MarkedPDFURL" : marked_pdf, "NumberOfGreenWords" : numberOfGreenwords, "NumberOfRednWords" : numberOfRedwords}
    return func.HttpResponse(
        json.dumps(resultJSON),
        mimetype="application/json",
    )
