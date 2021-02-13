from main import *



def run(request):
    print("Starting SweWindStatExcelLoader")
    file_name = ''
    file_name = '/Users/henrik/data/Godkända anläggningar_14cols50rows.xlsx'
    if file_name is not '':
        logging.info("Excel File=" + file_name)
        df = open_excel(file_name)
    else:
        fileUrl = "http://epi6.energimyndigheten.se/SharePoint/Eugen/Godkända anläggningar.xlsx"
        logging.info("URL=" + fileUrl)
        df = open_excel_url(fileUrl)

    print(df.to_csv(index=False))
    csvString = remove_mid_newlines(df.dropna(axis='columns').to_csv(index=False))
    print("###{}###".format(csvString))



def test_remove_mid_newline():
    csv = """Anläggningens namn,Organisationsnr,Företagsnamn,Innehav,Tilldelningsfaktor (%),Vid ansökan angiven normalårsproduktion (MWh),Förväntad elcertifikatberättigad produktion (MWh),Installerad effekt (kW),Energikälla,Typ,Nätområdes-ID,Elområde,"Slutdatum 
för tilldelning","Vid ansökan angivet
drifttagningsdatum produktionsenhet (vid flera enheter anges drifttagningsdatum för första och sista enhet)"
Privatperson,Privatperson,Privatperson,1 ägare,100.0,45,45,42.0,Sol,Sol,IKN,SE4,2030-07-07,2015-06-10 - 2015-06-10
Bergeforsen kraftstation,556044-8887,Bergeforsens Kraft AB,1 ägare,1.44,735000,10584,144000.0,Vatten,Vatten,SUR,SE2,2026-09-01,1955-10-07 - 1959-12-01
Privatperson,Privatperson,Privatperson,1 ägare,100.0,49,49,49.4,Sol,Sol,IKN,SE3,2027-02-06,2012-01-24 - 2016-04-22
Väby 1,556857-0591,Väby Driftintressenter AB,1 ägare,100.0,5400,5400,2000.0,Vind,Landbaserad,SYD,SE4,2026-12-27,2011-12-22 - 2011-12-22
Väby 2,556857-0591,Väby Driftintressenter AB,1 ägare,100.0,5400,5400,2000.0,Vind,Landbaserad,SYD,SE4,2027-02-08,2012-01-19 - 2012-01-19
"""
    print(remove_mid_newlines(csv))


#run(123)
test_remove_mid_newline()