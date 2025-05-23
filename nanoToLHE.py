import uproot
import pylhe
import sys
import vector
import awkward as ak
import tqdm
vector.register_awkward()

assert len(sys.argv) > 2, "Please provide input and output file names as arguments."
print("Reading LHE file from", sys.argv[1])
print("Writing LHE file to", sys.argv[2])

if len(sys.argv) == 5:
  start, stop = int(sys.argv[3]), int(sys.argv[4])
else:
  start, stop = 0, None
print("Processing events", start, "to", stop)

f = uproot.open(sys.argv[1])

fields = ["pt", "eta", "phi", "mass", "pdgId", "status", "spin"]
lhepart = f["Events"].arrays([f"LHEPart_{field}" for field in fields], library="ak", entry_start=start, entry_stop=stop)
events = ak.zip({field: lhepart[f"LHEPart_{field}"] for field in fields}, with_name="Momentum4D")

lheevents = []

for parts in tqdm.tqdm(events):
  lheeventinfo = pylhe.LHEEventInfo(
    nparticles = len(parts),
    pid = 0,
    weight = 1.0, # may need to be changed
    scale = 100.0, # may need to be changed
    aqed = 1/137, # may need to be changed
    aqcd = 0.1181 # may need to be changed
  )
  
  lheparticles = []
  for part in parts:
    lheparticle = pylhe.LHEParticle(
      id = part.pdgId,
      status = part.status,
      spin = part.spin,
      px = part.px,
      py = part.py,
      pz = part.pz,
      e = part.e,
      m = part.m,
      mother1 = 0, # can be extracted from genpart if needed
      mother2 = 0, # can be extracted from genpart if needed
      color1 = 0,
      color2 = 0,
      lifetime = 0
    )
    lheparticles.append(lheparticle)

  lheevent = pylhe.LHEEvent(
    eventinfo = lheeventinfo,
    particles = lheparticles,
  )
  lheevents.append(lheevent)

# no idea if all of this matters at all
lheinit = pylhe.LHEInit(
    initInfo=pylhe.LHEInitInfo(
        beamA=2212,
        beamB=2212,
        energyA=6.8,
        energyB=6.8,
        PDFgroupA=0,
        PDFgroupB=0,
        PDFsetA=0,
        PDFsetB=0,
        weightingStrategy=3,
        numProcesses=1,
    ),
    procInfo=[
        pylhe.LHEProcInfo(
            xSection=0,
            error=0,
            unitWeight=1,
            procId=1,
        )
    ],
    weightgroup={},
    LHEVersion=3,
)

pylhe.write_lhe_file(lheinit, lheevents, sys.argv[2])