import bento_mdf
import pandas as pd

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




# Use CDS model as experiment
modelfiles = ["https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/5.0.3/model-desc/cds-model.yml",
              "https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/5.0.3/model-desc/cds-model-props.yml"]

cds_mdf = bento_mdf.MDF(*modelfiles)

cds_nodes = cds_mdf.model.nodes
cds_edges = cds_mdf.model.edges

nodelist = list(cds_nodes.keys())

#edges: edgename, src name, dst name
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
        srclist.remove(srcname)
print(f"dstlist only: {dstlist}\nsrclist only: {srclist}")


#for edge in cds_edges:
#    print(f"Source: {edge.src}\tDst: {edge.dst}")


    
'''
for node in cds_nodes:
    reqfields = getKeyFields(node, cds_mdf)
    props = cds_mdf.model.nodes[node].props
    for prop in props.values():
        tempplatecheck = propTemplateCheck(prop, cds_mdf)
        print(str(tempplatecheck))
'''

