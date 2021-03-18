#include <iostream>
#include <fstream>
#include <cstdlib>

#include <TCanvas.h>
#include <TROOT.h>
#include <TApplication.h>

#include "Garfield/ViewCell.hh"
#include "Garfield/ViewDrift.hh"
#include "Garfield/ViewSignal.hh"

#include "Garfield/ComponentAnalyticField.hh"
#include "Garfield/MediumMagboltz.hh"
#include "Garfield/Sensor.hh"
#include "Garfield/DriftLineRKF.hh"
#include "Garfield/TrackHeed.hh"

using namespace Garfield;

int main(int argc, char * argv[]) { 

  TApplication app("app", &argc, argv);

  // Make a gas medium.
  MediumMagboltz gas;
  gas.LoadGasFile("ar_70-co2_30-1bar.gas");
  const std::string path = std::getenv("GARFIELD_HOME");
  gas.LoadIonMobility(path + "/Data/IonMobility_Ar+_Ar.txt");

  // Make a component with analytic electric field.
  ComponentAnalyticField cmp;
  cmp.SetMedium(&gas);
  // Wire radius [cm]
  const double rWire = 15.e-4;
  // Outer radius of the tube [cm]
  const double rTube = 0.49;
  // Voltages
  const double vWire = 1750.;
  const double vTube = 0.;
  // Add the wire in the centre.
  cmp.AddWire(0, 0, 2 * rWire, vWire, "s");
  // Add the tube.
  cmp.AddTube(rTube, vTube, 0, "t");
  // request calculation of signal induced on the wire. 
  cmp.AddReadout("s");

  // Make a sensor.
  Sensor sensor;
  //calculate the E field using cmp.
  sensor.AddComponent(&cmp);
  sensor.AddElectrode(&cmp, "s");
  // Set the signal time window.
  const double tstep = 0.5;
  const double tmin = -0.5 * tstep;
  const unsigned int nbins = 1000;
  sensor.SetTimeWindow(tmin, tstep, nbins);
  sensor.ClearSignal();

  // Set up Heed. Simulates ionisation produced by a charged
  //particle crossing the tube. (pion+ with  
  TrackHeed track;
  track.SetParticle("pi+"); //pion
  //energy unit GeV
  track.SetEnergy(20.e9); //suggested by Angela Romano, instead of 75GeV. Average Energy for 3 body decay
  track.SetSensor(&sensor);

  // RKF integration.
  DriftLineRKF drift;
  drift.SetSensor(&sensor);
  drift.SetGainFluctuationsPolya(0., 20000.);

  TCanvas* cD = nullptr;
  ViewCell cellView;
  ViewDrift driftView;
  constexpr bool plotDrift = true;
  if (plotDrift) {
    cD = new TCanvas("cD", "", 600, 600);
    cellView.SetCanvas(cD);
    cellView.SetComponent(&cmp);
    driftView.SetCanvas(cD);
    drift.EnablePlotting(&driftView);
    track.EnablePlotting(&driftView);
  } 

  TCanvas* cS = nullptr;
  ViewSignal signalView;
  constexpr bool plotSignal = true;
  if (plotSignal) {
    cS = new TCanvas("cS", "", 600, 600);
    signalView.SetCanvas(cS);
    signalView.SetSensor(&sensor);
    //signalView.SetLabelY("signal [fC]");
  } 

  /*
  cS = new TCanvas("cS", "", 600, 600);
  signalView.SetCanvas(cS);
  signalView.SetSensor(&sensor);
  */
// distance of track from wire centre [mm]
  const double rTrack = 0.99 * rTube * 6/10;
  const double x0 = rTrack;
  const double y0 = -sqrt(rTube * rTube - rTrack * rTrack);
  const unsigned int nTracks = 1;
  for (unsigned int j = 0; j < nTracks; ++j) {
    sensor.ClearSignal();
    track.NewTrack(x0, y0, 0, 0, 0, 1, 0);
    double xc = 0., yc = 0., zc = 0., tc = 0., ec = 0., extra = 0.;
    int nc = 0;
    while (track.GetCluster(xc, yc, zc, tc, nc, ec, extra)) {
      for (int k = 0; k < nc; ++k) {
        double xe = 0., ye = 0., ze = 0., te = 0., ee = 0.;
        double dx = 0., dy = 0., dz = 0.;
        track.GetElectron(k, xe, ye, ze, te, ee, dx, dy, dz);
        drift.DriftElectron(xe, ye, ze, te);
      }
    }
    if (plotDrift) {
      cD->Clear();
      cellView.Plot2d();
      constexpr bool twod = true;
      constexpr bool drawaxis = false;
      driftView.Plot(twod, drawaxis);
    }
    sensor.ConvoluteSignals();
    int nt = 0;
    if (!sensor.ComputeThresholdCrossings(-2., "s", nt)) continue;
    if (plotSignal) signalView.PlotSignal("s");
  }

  cD->SaveAs("drift_7030-6.pdf");
  cS->SaveAs("signal_7030-6.pdf");
  cD->SaveAs("drift_7030-6.C");
  cS->SaveAs("signal_7030-6.C");
  app.Run(kTRUE);

}