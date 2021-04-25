# PDFKeywordsMarker

This is a simple PDF keywords marker solution.
The solution is deployed as Azure Function and using Azure Storage.

![UML Sequence - Consumer Call](https://github.com/ronisc/PDFKeywordsMarker/blob/main/Documentation/UML%20Sequence%20-%20Consumer%20Call.PNG?raw=true)


# How To call the code:
Once the code is deployed (or running on your machine), 
use HTTP tester tool (like Postman) to call the ‘Mark’ method using HTTP POST

Example of payload:
```JSON
{
  "InputPDF_URL": "https://SomeValidURLWithPDF/thefilename.pdf",
  "GreenWords" : ["GreenWord1", "GreenWord2"],
  "RedWords" : ["RedWords1", "RedWords2"]
}
```