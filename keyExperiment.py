import bento_mdf
import pandas as pd
from collections import Counter

def getKeyFields(node, mdf):
    keylist = []
    edgelist = mdf.model.edges_by_src(mdf.model.nodes[node])
    for edge in edgelist:
        destnode = edge.dst.get_attr_dict()['handle']
        #Filter out this node, no need to self reference
        if destnode != node:
            destprops = mdf.model.nodes[destnode].props
            for destkey, destprop in destprops.items():
                if destprop.get_attr_dict()['is_key'] == 'True':
                    keylist.append(destnode+"."+destprop.get_attr_dict()['handle'])
    return keylist

def templateCheck(node, mdf):
    templatecheck = None
    props = mdf.model.nodes[node].props
    for prop in props.values():
        if 'Template' in prop.tags:
           templatecheck = prop.tags['Template'].get_attr_dict()['value']
    return templatecheck

def propTemplateCheck(prop, mdf):
    templatecheck = None
    if 'Template' in prop.tags:
        templatecheck = prop.tags['Template'].get_attr_dict()['value']
    return templatecheck

def getRootKey(edges):
    srclist = []
    dstlist = []
    for edgekey, edgeobj in edges.items():
        srclist.append(edgeobj.src.handle)
        dstlist.append(edgeobj.dst.handle)
    #Remove duplicates
    srclist = list(set(srclist))
    dstlist = list(set(dstlist))
    for srcname in srclist:
        if srcname in dstlist:
            dstlist.remove(srcname)
    if len(dstlist) != 1:
        return None
    else:
        return dstlist[0]
'''
def getRelations(searchkey, edges, relationships):
    rellist = []
    for edgekey in edges.keys():
        if searchkey in edgekey:
            rellist.append(edgekey)

    relationships[searchkey] = rellist
    return relationships
'''

def getDstNodes(searchnode, mdf, dstlist):
   # dstlist = []
    dstedges = mdf.model.edges_by_dst(mdf.model.nodes[searchnode])
    for dstedge in dstedges:
        dstlist.append(dstedge.src.handle)
    return dstlist


# Use CDS model as experiment
modelfiles = ["https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/5.0.3/model-desc/cds-model.yml",
              "https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/5.0.3/model-desc/cds-model-props.yml"]

cds_mdf = bento_mdf.MDF(*modelfiles)

cds_nodes = cds_mdf.model.nodes
cds_edges = cds_mdf.model.edges

nodelist = list(cds_nodes.keys())

#edges: edgename, src name, dst name
rootnode = getRootKey(cds_edges)

dstlist = []
dstlist = getDstNodes(rootnode, cds_mdf, dstlist)
checklist = []
while Counter(checklist) != Counter(dstlist):
    for dstnode in dstlist:
        if dstnode not in checklist:
            checklist.append(dstnode)
            dstlist = getDstNodes(dstnode, cds_mdf, dstlist)
            #print(checklist)
            print(f"DSTLIST: {dstlist}")
            print(f"CHECKLIST: {checklist}")
print(dstlist)


'''
step 1 get dst nodes for root
step 2 for each dst node, get their dst nodes
'''

#From root node find all destinations
#reltree = {}
#reltree = getRelations(rootnode, cds_edges, reltree)
#Get all the edges with rootnode as destination
#[print(dstkey.triplet) for dstkey in cds_mdf.model.edges_by_dst(cds_mdf.model.nodes[rootnode])]
#dstedges = cds_mdf.model.edges_by_dst(cds_mdf.model.nodes[rootnode])
#print(dstedges.src.handle)
#srclist = []
#checkedlist = []
#for dstedge in dstedges:
#    srclist.append(dstedge.src.handle)

#    print(dstedge.get_attr_dict())j
    #print(dstedge.src.handle)
    #print(dstedge.dst.handle)




'''
srclist = []
dstlist = []
for edgekey, edgeobj in cds_edges.items():
    print(edgekey)
    print(f"Source: {edgeobj.src.handle}\tDst: {edgeobj.dst.handle}")
    #print(edgeobj.get_attr_dict())
    srclist.append(edgeobj.src.handle)
    dstlist.append(edgeobj.dst.handle)
srclist = set(srclist)
dstlist = set(dstlist)
#for dstname in dstlist:
#    if dstname in srclist:
#        srclist.remove(dstname)
for srcname in list(srclist):
    if srcname in dstlist:
        dstlist.remove(srcname)
        #srclist.remove(srcname)
#print(f"dstlist only: {dstlist}\nsrclist only: {srclist}")
rootnode = dstlist[0]



#for edge in cds_edges:
#    print(f"Source: {edge.src}\tDst: {edge.dst}")

'''
    
'''
for node in cds_nodes:
    reqfields = getKeyFields(node, cds_mdf)
    props = cds_mdf.model.nodes[node].props
    for prop in props.values():
        tempplatecheck = propTemplateCheck(prop, cds_mdf)
        print(str(tempplatecheck))
'''

