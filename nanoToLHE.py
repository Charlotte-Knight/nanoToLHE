import uproot
import pylhe
import sys
import awkward as ak
import numpy as np

assert len(sys.argv) > 2, "Please provide input and output file names as arguments."
print("Reading LHE file from", sys.argv[1])
print("Writing LHE file to", sys.argv[2])

if len(sys.argv) == 5:
  start, stop = int(sys.argv[3]), int(sys.argv[4])
else:
  start, stop = 0, None
print("Processing events", start, "to", stop)

print("Loading events from file")
f = uproot.open(sys.argv[1])
fields = ["pt", "eta", "phi", "mass", "pdgId", "status", "spin"]
events = f["Events"].arrays([f"LHEPart_{field}" for field in fields], library="ak", entry_start=start, entry_stop=stop)
nLHEPart = f["Events/nLHEPart"].array(library="ak", entry_start=start, entry_stop=stop)

lheevents = np.empty(len(events), dtype=object)
idx = np.arange(len(events))

print("Creating LHE events")
for n in np.unique(nLHEPart):
  sevents = events[nLHEPart == n]
  sidx = idx[nLHEPart == n]

  px = sevents["LHEPart_pt"].to_numpy() * np.cos(sevents["LHEPart_phi"].to_numpy())
  py = sevents["LHEPart_pt"].to_numpy() * np.sin(sevents["LHEPart_phi"].to_numpy())
  pz = sevents["LHEPart_pt"].to_numpy() * np.sinh(sevents["LHEPart_eta"].to_numpy())
  e = np.sqrt(sevents["LHEPart_mass"].to_numpy()**2 + px**2 + py**2 + pz**2)
  m = sevents["LHEPart_mass"].to_numpy()
  pdgId = sevents["LHEPart_pdgId"].to_numpy()
  status = sevents["LHEPart_status"].to_numpy()
  spin = sevents["LHEPart_spin"].to_numpy()

  for i in range(len(sevents)):
    lheeventinfo = pylhe.LHEEventInfo(
      nparticles = n,
      pid = 0, # may need to be changed
      weight = 1.0, # may need to be changed
      scale = 100.0, # may need to be changed
      aqed = 1/137, # may need to be changed
      aqcd = 0.1181 # may need to be changed
    )

    lheparticles = []
    for j in range(n):
      lheparticle = pylhe.LHEParticle(
        id = pdgId[i][j],
        status = status[i][j],
        spin = spin[i][j],
        px = px[i][j],
        py = py[i][j],
        pz = pz[i][j],
        e = e[i][j],
        m = m[i][j],
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
    lheevents[sidx[i]] = lheevent

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

print("Writing lhe")
pylhe.write_lhe_file(lheinit, lheevents, sys.argv[2])