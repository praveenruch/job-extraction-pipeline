001- HTML to Text Conversion
## Status
Proposed
Decision Date: 2024-06-15

## Context
As of now we are using beautiful soup to convert HTML to text.  The way the these tool works is that they only parse then text 
and remove the tags and the attributes values that the tag have. This is not ideal in our case because the way Hacker News  format there posts is that 
truncate the link in text part of <a></a> tags when they are too long. The current links address is part of the href attribute but they are sometimes truncated in text.

So we need a way to preserve the link address in the text conversion process. We need to find a way to convert HTML while preserving the link addresses,

## Data we found.

1. We parsed data for September for all job posting from Hacker News.
2. 247 total job entries were found the month of September.
3. Out of the 247 job entries total of 67 job entries had at least one link where the text was truncated.
4. This makes up 27% of the total job entries for September from the small sample we found. This is a significant number of job entries that have truncated links in the text part of the <a></a> tags.

## Options
1. Use Beautiful Soup to parse the HTML and extract the text, but also extract the href attribute of the <a> tags and replace the text with the actual link address.
    Pros : data is preserved, not additional data structure 
    Cons: More effort
2. Parse it and store it separately in a different field or data structure. 
    Pros: data is preserved, data is searate from original data
    Cons: additional data structure, more complex to query and use the data, loose context.
3. Parse and add it at the end of the document.
    Pros: data is preserved, not additional data structure 
    Cons: More effort, loose context.

## Decision
Go with Option 1 , initial effort but not more effort after the parsing is done.  The data is preserved and we don't have to create additional data structures.  

