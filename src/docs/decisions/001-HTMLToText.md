001- HTML to Text Conversion
## Status
Proposed
Decision Date: 2024-06-15

### Context
In our application, we need to convert the job description HTML downloaded from various sources into plain text for further processing and analysis. The HTML content may contain various tags, styles, and scripts that are not relevant to the text extraction process. Therefore, we need a reliable method to convert HTML to plain text while preserving the meaningful content. 
We are using BeautifulSoup, a Python library, to parse the HTML and extract the text content. However, we need to ensure that the conversion process is efficient and handles different HTML structures effectively.
The problem with Beautiful Soup is that 
1. When you convert to text using get_text() method, it removes all the href values from a tags, which are important for our use case. We need to preserve the href values while converting the HTML to text.
2. The text in href is truncated when they are too long effectively loosing the information in the href. We need to ensure that the full href values are preserved in the text output.

### Options Considered
1. copy the href values to the text output while converting HTML to text using BeautifulSoup's get_text() method. This can be done by modifying the get_text() method to include the href values in the output.
   Pros:keeps the location and context of the links in the text output, which can be useful for further processing and analysis.
   Cons: This approach may result in a cluttered text output, especially if there are many links in the HTML content. It may also require additional processing to extract the href values from the text
2. Copy all href values into a separate list or dictionary while converting HTML to text using BeautifulSoup's get_text() method. This way, we can preserve the href values separately and use them as needed.
   Pros: Keeps the href values separate from the text output, which can be useful for further processing and analysis. It also allows us to easily access the href values without having to parse the text output.
   Cons: Loose the context, will need some additional processing to associate the href values with their corresponding text in the output.
3. Move them to a different section when parsing the document.
    Pros: Keeps the href values separate from the text output, which can be useful for further processing and analysis. It also allows us to easily access the href values without having to parse the text output.
    Cons: Loose the context, will need some additional processing to associate the href values with their corresponding text in the output.
4. Do not parse the a tags at all and leave then as is for later use. This way, we can preserve the href values in their original form and use them as needed.
   Pros: Keeps the href values in their original form, which can be useful for further processing and analysis. It also allows us to easily access the href values without having to parse the text output.
   Cons: Extra effort to not parse a tags. Not sure if supported by library.

#### Decision
We have decided to implement option 1, which involves modifying the get_text() method to include the href values in the output. This approach allows us to preserve the location and context of the links in the text output, which can be useful for further processing and analysis. We will ensure that the full href values are preserved in the text output, even if they are long, to avoid losing any important information.
