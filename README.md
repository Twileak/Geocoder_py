# Geocoder
In this programme me, along with 2 other people, are trying to alter a plug-in for QGIS. The main feature we want to adress is situation, when geocoding returns more than 1 set of geographical coordinates for specific adress, The original solution was to choose the first returned value. we, however, are trying to choose the correct one by including postal code in the function. For now, this programme takes a csv file containing adresses, returns geographical coordinates and writes them to one of 3 files:
1. Lines, where some kind of error occured
2. Lines, where single value was returned
3. Lines, where more than one values where returned. Here we obtain all the coordinates reutrned by the function.

Down the line, I am going to include postal code as a key in choosing desired coordinates and then we wil use written programme in application while writing my Thesis "application of Traveling Salesmen dilemma"
