# Based on Bruce Wang's code
import bento_mdf
from crdclib import crdclib
import argparse
import pandas as pd
import random
import string

#
# Would it be better to implment the graph as a dataclass?
# Or a collection of dataclasses?  Node as class, props as entries
# Answer: Maybe not, dataclasses seem to not offer any real benefit over pandas for this
#


def getCDEIDVersion(node, prop, mdf):
    #print(f"Checking Node: {node}\tProp: {prop}")
    if mdf.model.props[(node,prop)].concept is not None:
        workingterms = mdf.model.props[(node,prop)].concept.terms.values()
        for workingtermobj in workingterms:
            workingterm = workingtermobj.get_attr_dict()
            cdeid = workingterm['origin_id']
            if 'origin_version' in workingterm:
                version = workingterm['origin_version']
                #Need to clean up some labelling mistakes
                if 'https' in version:
                    temp = version.split('=')
                    version = temp[-1]
            else:
                version = '1.00'
        return {"id": cdeid, "version": version}
    else:
        return {"id": None, "version": None}
    

def getCDEPVs(cde_json):
    #Returns a list of permissible values.  Returns None if no PVs are found
    pvlist = []
    if cde_json['DataElement']['ValueDomain']['type'] == 'Enumerated':
        for pv in cde_json['DataElement']['ValueDomain']['PermissibleValues']:
            pvlist.append(pv['value'])
    return pvlist
    
def getTermDictionary(property_terms):
    for term_object in property_terms.values():
        return term_object.get_attr_dict()


def populateProps(df, prop, prefix, pvlist, countlimit):
    counter = 0
    print(f"PVlist: {pvlist}\tType: {type(pvlist)}")
    while counter < countlimit:
        #if pvlist is None:
        #    randvalue = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        if len(pvlist) > 0:
        #if pvlist is not None:
            randvalue = random.choice(pvlist)
        else:
            randvalue = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        #if prefix is not None:
        #    randvalue = prefix+randvalue
        df.loc[counter, prop] = randvalue
        counter = counter+1
    return df



def main(args):
    #Get the configurations
    configs = crdclib.readYAML(args.configfile)

    #Read the MDF files.  Locations for MDF are from the config file.
    mdffiles = configs['mdffiles']
    mdfmodel = bento_mdf.MDF(*mdffiles, handle=configs['handle'])

    #Read the config file
    dataconfig = crdclib.readYAML(configs["nodefile"])
    rootnode = dataconfig['HeadNode'][0]['name']
    startnodes = dataconfig['IncludeNodes']
    node_list = [rootnode]
    for node, data in startnodes.items():
        if data['NodeCount'] > 0:
            node_list.append(node)
    
        
    # Now for the fun part, create the df_dictionary where the key is the node, and the value is a dataframe
    df_dictionary = {}
    for node in node_list:
        df_dictionary[node] = pd.DataFrame(columns=dataconfig['IncludeProperties'][node])

    # For each dataframe, add the number of rows
    for node, df in df_dictionary.items():
        prefix = None
        if node == rootnode:
             rowcount = 1
        else:
            rowcount = dataconfig['IncludeNodes'][node]['NodeCount']
            if dataconfig['IncludeNodes'][node]['Prefix'] is not None:
                prefix = dataconfig['IncludeNodes'][node]['Prefix']

        #Go through the props in each df
        props = list(df.columns.values)
        for prop in props:
            #Step 0, set up stuff
            pvlist = []
            # Step 1 get the CDE info if it exists
            #propobj = mdfmodel.model.props[(node,prop)]
            cdeinfo = getCDEIDVersion(node, prop, mdfmodel)
            print(f"Prop: {prop}\t Info: {str(cdeinfo)}")
            #Step 2 Use the cde info to find out if there are PVs.
            
            if cdeinfo['id'] is not None:
                cdejson = crdclib.getCDERecord(cdeinfo['id'], cdeinfo['version'])
                pvlist = getCDEPVs(cdejson)
            #Step 3, Populate the node sheet for this property
            df = populateProps(df, prop, prefix, pvlist, rowcount)
        df_dictionary[node] = df

    #Print out the dataframes
    for node, df in df_dictionary.items():
        filename = configs['outputpath']+str(node)+"_Loading.csv"
        df.to_csv(filename, sep="\t", index=False)
    
    # Create a datafrom from an Excel that has column names and a list of provided values in the columns
    #provided_df = pd.read_excel(configs['providedvaluesfile'],sheet_name=configs['sheetname'])


    '''   
    # for each load sheet, go field by field and 1) load with permissible values if they exist 2) Load with fake values if no PV.
    for node, proplist in node_headers.items():
        #need a dictionary to hold property:pvs
        temp_values = {}
        for prop in proplist:
            # If there is a CDE, it is in a Term annotation on the property
            if args.verbose:
                print(f"Node:\t{node}\tProperty:\t{prop}")
            if mdfmodel.model.props[(node,prop)].concept is not None:
                prop_terms= mdfmodel.model.props[(node,prop)].concept.terms
                term_dictionary = getTermDictionary(prop_terms)
                if 'origin_id' in term_dictionary:
                    cdejson = crdclib.getCDERecord(term_dictionary['origin_id'], term_dictionary['origin_version'])
                    pvlist = getCDEPVs(cdejson)
                    if pvlist is not None:
                        temp_values[prop] = pvlist
                    else:
                        temp_values[prop] = None
            else:
                temp_values[prop] = None
        #Set a number of rows to populate
        # TODO: This should be a user defined number
        rowcount = 10
        counter = 1
        while counter <= rowcount:
            line = {}
            for prop in proplist:
                #First use any provided values
                if prop in provided_df:
                    templist = provided_df[prop].to_list()
                    line[prop] = random.choice(templist)
                #If values weren't provided, check if there are permissible values
                elif temp_values[prop] is not None:
                    if len(temp_values[prop]) > 0:
                        line[prop] = random.choice(temp_values[prop])
                    else:
                        line[prop] = counter
                #And if neither of the first two worked, just add the counter number
                # TODO: Probably need some sort of random character generator
                else:
                    line[prop] = str(counter)
            df_dictionary[node].loc[len (df_dictionary[node])] = line
            counter = counter + 1
    for node, df in df_dictionary.items():
        filename = configs["outputpath"]+configs["outputname"]+"_"+node+".csv"
        df.to_csv(filename, sep="\t", index=False)
'''              
                
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-v", "--verbose", help="Verbose Output")

    args = parser.parse_args()

    main(args)