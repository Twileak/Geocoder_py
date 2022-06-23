# Geocoder
In this programme me, along with 2 other people, are trying to alter a plug-in for QGIS. The task of the plug - in is to take initial parameters as a written adress(city, street, number) and return geographical coordinates of this place. The main feature we want to adress is situation, when geocoding returns more than 1 set of geographical coordinates for specific adress, The original solution was to choose the first returned value. we, however, are choosing the correct one by including postal code in the function. For now, this programme takes a csv file containing adresses, returns geographical coordinates and writes them to one of 3 files:
1. Lines, where some kind of error occured
2. Lines, where single value was returned
3. Lines, where more than one values where returned. Here we obtain all the coordinates reutrned by the function.

