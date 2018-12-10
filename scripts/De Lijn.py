from scripts.Agency import Agency

query = '''
[out:xml][timeout:90];
(
  relation["operator"="De Lijn"]["ref"="305"];
);
(._;<;);
(._;>>;);
out meta;'''

delijn = Agency(name='De Lijn',
                zone_tag='zone:De_Lijn',
                ref_tag='ref:De_Lijn',
                route_ref_tag='route_ref:De_Lijn')

delijn.perform_overpass_query(query)
#delijn.fetch_agency_data(
#    sheet_url="https://docs.google.com/spreadsheet/ccc?key=1PGgEqobO90Mf9NsJHO1-JD-Npte1fYztK30HO5lRDI8&output=xls")
delijn.load_agency_data()
delijn.update_using_operator_data()
delijn.send_to_josm()
