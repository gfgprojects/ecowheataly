
"""
PM2.5 CF Addition to ReCiPe 2016 (Particulate Matter Formation)

The script manually adds PM2.5 characterization factors (CF) to the
ReCiPe 2016 Midpoint method ('Particulate Matter Formation', 'Egalitarian') and
ReCiPe 2016 Midpoint method ('Particulate Matter Formation', 'Egalitarian')

Use this script only once, before runnign the other scripts.

Reason: ReCiPe 2016 may omit PM2.5 CFs,
causing underestimation of particulate matter impacts.
Hence, the script:

finds PM2.5 flows from biosphere3,

Adds CF = 1.0 to these flows.

Writes the updated method without validate() (to bypass voluptuous issues).

Important Notes : Run Once: Avoid duplicates or overwrites.

Requires biosphere3 and ReCiPe 2016 methods pre-loaded.
"""
import bw2data as bd
# Load biosphere database
bs3 = bd.Database("biosphere3")

pmname =  ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Particulate Matter Formation', 'Egalitarian')
pm_method = bd.Method(pmname)

existing_cfs = pm_method.load()
# for cf in existing_cfs:
	# print(cf)
# Cerco PM2.5 nella biosfera
pm25_flows = [act for act in bs3 if 'Particulate Matter, < 2.5 um' in act['name']]
# for flow in pm25_flows:
#     print(f"Name: {flow['name']}, Code: {flow['code']}, category:{flow['categories']}")
pm25_codes = [flow['code'] for flow in pm25_flows]
# assegno i CF
for pm25_code in pm25_codes:
	flow = bs3.get(pm25_code)
	existing_cfs.append(((flow['database'], flow['code']), 1.0))


# pm_method.validate(existing_cfs)
pm_method.write(existing_cfs)

# Endpoint
pmname = ('ReCiPe 2016',  '1.1 (20180117)',  'Endpoint',  'Human health',  'Particulate Matter Formation', 'Egalitarian')
pm_method = bd.Method(pmname)

existing_cfs = pm_method.load()
# for cf in existing_cfs:
# 	print(cf)
# Cerco PM2.5 nella biosfera
pm25_flows = [act for act in bs3 if 'Particulate Matter, < 2.5 um' in act['name']]
# for flow in pm25_flows:
#     print(f"Name: {flow['name']}, Code: {flow['code']}, category:{flow['categories']}")
pm25_codes = [flow['code'] for flow in pm25_flows]
# assegno i CF
for pm25_code in pm25_codes:
	flow = bs3.get(pm25_code)
	existing_cfs.append(((flow['database'], flow['code']), 1.0))


# pm_method.validate(existing_cfs)
pm_method.write(existing_cfs)
