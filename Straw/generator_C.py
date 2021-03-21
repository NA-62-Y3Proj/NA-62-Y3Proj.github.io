#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

@author: Filippo Falezza
<filippo dot falezza at outlook dot it>
<fxf802 at student dot bham dot ac dot uk>

Released under GPLv3 and followings
"""

from sys import argv as sysargv
import shlex
import math
import numpy as np

#variables
gasfile = "ar_50-co2_50-1bar.gas"
name_base = "5050"

for i in range(1,11):
    name_range = f'{name_base}-{i}'
    distance = int(i) #set n coeffcient of the n/10 fraction
    #text
    text = f'#include <iostream>\n\
    #include <fstream>\n\
    #include <cstdlib>\n\n\
    #include <TCanvas.h>\n\
    #include <TROOT.h>\n\
    #include <TApplication.h>\n\n\
    #include "Garfield/ViewCell.hh"\n\
    #include "Garfield/ViewDrift.hh"\n\
    #include "Garfield/ViewSignal.hh"\n\n\
    #include "Garfield/ComponentAnalyticField.hh"\n\
    #include "Garfield/MediumMagboltz.hh"\n\
    #include "Garfield/Sensor.hh"\n\
    #include "Garfield/DriftLineRKF.hh"\n\
    #include "Garfield/TrackHeed.hh"\n\n\
    using namespace Garfield;\n\n\
    int main(int argc, char * argv[]) {{ \n\
      TApplication app("app", &argc, argv);\n\n\
      // Make a gas medium.\n\
      MediumMagboltz gas;\n\
      gas.LoadGasFile("{gasfile}");\n\
      const std::string path = std::getenv("GARFIELD_HOME");\n\
      gas.LoadIonMobility(path + "/Data/IonMobility_Ar+_Ar.txt");\n\n\
      // Make a component with analytic electric field.\n\
      ComponentAnalyticField cmp;\n\
      cmp.SetMedium(&gas);\n\
      // Wire radius [cm]\n\
      const double rWire = 15.e-4;\n\
      // Outer radius of the tube [cm]\n\
      const double rTube = 0.49;\n\
      // Voltages\n\
      const double vWire = 1750.;\n\
      const double vTube = 0.;\n\
      // Add the wire in the centre.\n\
      cmp.AddWire(0, 0, 2 * rWire, vWire, "s");\n\
      // Add the tube.\n\
      cmp.AddTube(rTube, vTube, 0, "t");\n\
      // request calculation of signal induced on the wire. \n\
      cmp.AddReadout("s");\n\n\
      // Make a sensor.\n\
      Sensor sensor;\n\
      //calculate the E field using cmp.\n\
      sensor.AddComponent(&cmp);\n\
      sensor.AddElectrode(&cmp, "s");\n\
      // Set the signal time window.\n\
      const double tstep = 0.5;\n\
      const double tmin = -0.5 * tstep;\n\
      const unsigned int nbins = 1000;\n\
      sensor.SetTimeWindow(tmin, tstep, nbins);\n\
      sensor.ClearSignal();\n\n\
      // Set up Heed. Simulates ionisation produced by a charged\n\
      //particle crossing the tube. (pion+ with  \n\
      TrackHeed track;\n\
      track.SetParticle("pi+"); //pion\n\
      //energy unit GeV\n\
      track.SetEnergy(20.e9); //suggested by Angela Romano, instead of 75GeV. Average Energy for 3 body decay\n\
      track.SetSensor(&sensor);\n\n\
      // RKF integration.\n\
      DriftLineRKF drift;\n\
      drift.SetSensor(&sensor);\n\
      drift.SetGainFluctuationsPolya(0., 20000.);\n\n\
      TCanvas* cD = nullptr;\n\
      ViewCell cellView;\n\
      ViewDrift driftView;\n\
      constexpr bool plotDrift = true;\n\
      if (plotDrift) {{\n\
        cD = new TCanvas("cD", "", 600, 600);\n\
        cellView.SetCanvas(cD);\n\
        cellView.SetComponent(&cmp);\n\
        driftView.SetCanvas(cD);\n\
        drift.EnablePlotting(&driftView);\n\
        track.EnablePlotting(&driftView);\n\
      }} \n\n\
      TCanvas* cS = nullptr;\n\
      ViewSignal signalView;\n\
      constexpr bool plotSignal = true;\n\
      if (plotSignal) {{\n\
        cS = new TCanvas("cS", "", 600, 600);\n\
        signalView.SetCanvas(cS);\n\
        signalView.SetSensor(&sensor);\n\
        //signalView.SetLabelY("signal [fC]");\n\
      }} \n\n\
      /*\n\
      cS = new TCanvas("cS", "", 600, 600);\n\
      signalView.SetCanvas(cS);\n\
      signalView.SetSensor(&sensor);\n\
      */\n\
    // distance of track from wire centre [mm]\n\
      const double rTrack = 0.99 * rTube * {distance}/10;\n\
      const double x0 = rTrack;\n\
      const double y0 = -sqrt(rTube * rTube - rTrack * rTrack);\n\
      const unsigned int nTracks = 1;\n\
      for (unsigned int j = 0; j < nTracks; ++j) {{\n\
        sensor.ClearSignal();\n\
        track.NewTrack(x0, y0, 0, 0, 0, 1, 0);\n\
        double xc = 0., yc = 0., zc = 0., tc = 0., ec = 0., extra = 0.;\n\
        int nc = 0;\n\
        while (track.GetCluster(xc, yc, zc, tc, nc, ec, extra)) {{\n\
          for (int k = 0; k < nc; ++k) {{\n\
            double xe = 0., ye = 0., ze = 0., te = 0., ee = 0.;\n\
            double dx = 0., dy = 0., dz = 0.;\n\
            track.GetElectron(k, xe, ye, ze, te, ee, dx, dy, dz);\n\
            drift.DriftElectron(xe, ye, ze, te);\n\
          }}\n\
        }}\n\
        if (plotDrift) {{\n\
          cD->Clear();\n\
          cellView.Plot2d();\n\
          constexpr bool twod = true;\n\
          constexpr bool drawaxis = false;\n\
          driftView.Plot(twod, drawaxis);\n\
        }}\n\
        sensor.ConvoluteSignals();\n\
        int nt = 0;\n\
        if (!sensor.ComputeThresholdCrossings(-2., "s", nt)) continue;\n\
        if (plotSignal) signalView.PlotSignal("s");\n\
      }}\n\n\
      cD->SaveAs("drift_{name_range}.pdf");\n\
      cS->SaveAs("signal_{name_range}.pdf");\n\
      cD->SaveAs("drift_{name_range}.C");\n\
      cS->SaveAs("signal_{name_range}.C");\n\
      app.Run(kTRUE);\n\n\
    }}'

    #target file
    targetfile = f'signal-{name_range}.C'
    target = open(targetfile, "x")
    target.write(text)
    target.close()
    print("Target file correctly written")


print("end of the loop")
exit(0)
