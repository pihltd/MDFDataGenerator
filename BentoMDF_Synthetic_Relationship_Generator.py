#This generates the relationship files needed for the Synthetic Data Generator
# It can use the same config file as the data generator
import argparse
import bento_mdf
from crdclib import crdclib
import pandas as pd
import sys

def findHeadNode(edges):
    # In theory, a node that is only a source, not a destintation, should be the root node
    srclist = []
    dstlist =[]
    for edjeobj in edges.values():
        srclist.append(edjeobj.src.handle)
        dstlist.append(edjeobj.dst.handle)
    #Remove any duplicates
    srclist = list(set(srclist))
    dstlist = list(set(dstlist))
    
    for src in srclist:
        if src in dstlist:
            dstlist.remove(src)
    return dstlist

    

def main(args):
    #Get the configs
    configs = crdclib.readYAML(args.configfile)
    
    #Read the model
    mdffiles = configs['mdffiles']
    mdfmodel = bento_mdf.MDF(*mdffiles, handle=configs['handle'])
    
    #Set up dataframes
    columns = ["handle", "source", "target", "relationship"]
    edge_df = pd.DataFrame(columns=columns)
    finaldict = {}
    
    #Get the edge relationships which are  {(relationship name, source, target), edge object}
    edges = mdfmodel.model.edges
    #Get the nodes which are { nodename: node object}
    nodes = mdfmodel.model.nodes
    
    # The easiest way to deal with relationships is going to be a datafram
    for info, edgeobj in edges.items():
        edge_df.loc[len(edge_df)] = {"handle": info[0], "source": info[1], "target": info[2], "relationship": edgeobj.get_attr_dict()['multiplicity']}

    rootnodes = findHeadNode(edges)
    if len(rootnodes) !=1:
        print(rootnodes)
        #rootnode = None
        sys.exit(0)
    else:
        rootnode = rootnodes[0]
    
    #Need a root node and it should be program
    finaldict['HeadNode'] = [{"name": rootnode, "count": 1, "Prefix": configs['handle']}]
    nodelist = list(nodes.keys())
    #print(nodelist)
    temp = {}
    proptemp = {}
    
    # Populate the IncludeNodes and IncludeProperties sections
    # TODO:  Need to handle rootnode so that properties are included in proplist
    for node in nodelist:
        if node != rootnode:
            temp[node] = {"NodeCount":"", "Prefix":""}
        #temp[node] = {"NodeCount":"", "Prefix":""}
        nodeprops = nodes[node].props
        proplist = []
        #Yank out anything that's Template:No
        #NOTE: THIS ALSO REMOVES REQUIRED ID COLUMNS
        # Need to keep Template:No, Key:true fields  I think.
        for propkey, propobj in nodeprops.items():
            if 'Template' in propobj.tags:
                if (propobj.tags['Template'].get_attr_dict()['value'] != 'No'):
                    proplist.append(propkey)
            else:
                proplist.append(propkey)
        proptemp[node] = proplist

    finaldict['IncludeNodes'] = temp
    finaldict['IncludeProperties'] = proptemp
    
    # Add the relationships.  Note, this differs significantly from Bruce's representation
    
    #reltemp = {}
    #sourcelist = edge_df['source'].unique()
    #for source in sourcelist:
    #    rowtemp = {}
    #    source_df = edge_df.loc[edge_df['source'] == source]
    #    for row in source_df.iterrows():
    #        print(row)
    #        rowtemp['target'] = row['target']
    #        rowtemp['relationship'] = row['relationship']
    #    reltemp[source] = rowtemp
    #finaldict['RelationshipSpecs'] = reltemp
    
    filename = configs['outputpath']+configs['outputname']
    crdclib.writeYAML(filename, finaldict)
    
       


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-v", "--verbose", help="Verbose Output")

    args = parser.parse_args()

    main(args)