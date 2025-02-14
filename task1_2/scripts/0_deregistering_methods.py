#exec(open('deregistering_methods.py').read())
import bw2data as bd
print("deregistering newly created methods")

ecow=[m for m in bd.methods if 'ecowheataly' in str(m)]

for mt in ecow:
    bd.Method(mt).deregister()

