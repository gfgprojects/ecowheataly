#exec(open('deregistering_methods.py').read())
print("deregistering newly created methods")

ecow=[m for m in bd.methods if 'ecowheataly' in str(m)]

for mt in ecow:
    bd.Method(mt).deregister()

