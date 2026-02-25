# AI use case, product, platform, and model catalogue

We have many user needs related to a catalogue:

* Catalogue of assured tools/platorms
* Catalogue of tools in use
* List of where models are used in which platforms
* SRO for a product or tool
* assurance documentation
* A CRM for what we know about tools or products on the market

...and so on. We have informatica which is our enterprise data catalogue, we have Ardoq which is our architecture and platform data set, we have Atamis for contract data, but all of these are parts of the puzzle I want to solve specifically for AI products.

## Proposed solution

Build a Django platform for people to work in that would solve all the above user needs. Include an API aspect so we can properly integrate (both in and out, push and pull) to other places like Ardoq or Informatica.

Have a public front-end which acts like a nutrition label for AI uses, shows what tools we have and what they are for.

The data set would capture:

## Model

* Training cutoff date
* Context size
* Developer organisation
* Token size
* and so on... I want this to be relatively comprehensive

## Tool/Platform

* Developer org
* Use case
* links to contract information in ardoq
* links to data sets in informatica
* and so on...

You should refer to this ontology for the "type of information" which we would want to capture <https://github.com/kelcey-caboff/ai-ontology>. You do not need to follow this ontology to the letter, it is more of a vibe-guide.

## Plan

Build this containerised with a docker-compose to codify it and using PostgreSQL as the database. Give it a nice "coat of paint" for the templates and styling.