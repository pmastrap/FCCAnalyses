# quick script checking efficiencies in the bbWW(lvlv) channel, with the new delphes card

from collections import namedtuple
import ROOT
import argparse
import os 
import matplotlib.pyplot as plt
from array import array

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)


def check_truth_brs(input_filepath, out_dir_base, plot_format=".png"):

	if not os.path.exists(out_dir_base):
		os.mkdir(out_dir_base)

	rdf = ROOT.RDataFrame("events", input_filepath)

	if not rdf:
		print("Empty file for:", input_filepath, " Exiting.")
		return

	#get the number of truth leptons from W(decay): 
	nevts_all = rdf.Count().GetValue()
	print("All evts", nevts_all)
	nevts_full_had = rdf.Filter("n_truth_leps_from_HWW == 0").Count().GetValue()
	nevts_full_had_rel = nevts_full_had/nevts_all*100.
	print("0 leps from W decay {} = {:.2f} %".format(nevts_full_had, nevts_full_had_rel))
	nevts_1lep = rdf.Filter("n_truth_leps_from_HWW == 1").Count().GetValue()
	nevts_1lep_rel = nevts_1lep/nevts_all*100.
	print("1 leps from W decay {} = {:.2f} %".format(nevts_1lep, nevts_1lep_rel))
	nevts_2lep = rdf.Filter("n_truth_leps_from_HWW == 2").Count().GetValue()
	nevts_2lep_rel = nevts_2lep/nevts_all*100.
	print("2 leps from W decay {} = {:.2f} %".format(nevts_2lep, nevts_2lep_rel))
	checker = nevts_full_had_rel+nevts_1lep_rel+nevts_2lep_rel
	print("Checking total", checker)
	print("Checking maximum two:", rdf.Filter("n_truth_leps_from_HWW > 2").Count().GetValue())

def get_rdf(input_filepath):

	rdf = ROOT.RDataFrame("events", input_filepath)
	if not rdf:
		print("Empty file for:", input_filepath, " Exiting.")
		return
	return rdf


def check_photon_res_per_eta_bin(input_rdf, cutstring_base, E_edges, hist_name, filebasename, out_dir_base):

	model = ROOT.RDF.TH1DModel("resolution_model_hist", "resolution_model_hist", 40, -0.05, 0.05)

	#histogram vs E
	hist_binEdges = array("d", E_edges)
	hist_nBins = len(E_edges)-1
	hist_res_vs_E = ROOT.TH1D(filebasename, filebasename, hist_nBins, hist_binEdges)

	rdf_bin = input_rdf.Filter(cutstring_base)
	rdf_resolution = rdf_recomatch.Define('lep_resolution', '(E_truthmatched_leps_from_HWW_noiso[0] - E_truth_leps_from_HWW[0])/E_truth_leps_from_HWW[0]')

	for i_E_edge in range(len(E_edges)-1):
		cutstring_bin = "E_truthmatched_leps_from_HWW_noiso[0] > {:.2f} && E_truthmatched_leps_from_HWW_noiso[0] <= {:.2f}".format(E_edges[i_E_edge], E_edges[i_E_edge+1])
		rdf_bin = rdf_resolution.Filter(cutstring_bin)

		#store a histogram of the resolution 
		tmp_hist = rdf_bin.Histo1D(model, 'lep_resolution').GetValue()   
		histfilename = "{}_E_{}_to_{}".format(filebasename, E_edges[i_E_edge], E_edges[i_E_edge+1])
		tmp_hist.SetTitle("{}, RMS = {:.4f}".format(hist_name, tmp_hist.GetRMS()) )     
		gaus_pars = plot_single_hist(tmp_hist, histfilename, out_dir_base, "#sigma(E)/E", colour_code=38, file_format="png")
		
		# hist_res_vs_E.SetBinContent(i_E_edge+1, tmp_hist.GetRMS())
		if gaus_pars:
			hist_res_vs_E.SetBinContent(i_E_edge+1, gaus_pars[2])
			hist_res_vs_E.SetBinError(i_E_edge+1, gaus_pars[3])

	plot_single_hist(hist_res_vs_E, filebasename, out_dir_base, "E_{true} in GeV", colour_code=38, file_format="png")
	# plot_2D(rdf_resolution, 'pT_truthmatched_ys_from_higgs_noiso', 'y_resolution', out_dir_base)	

	
	return hist_res_vs_E

def check_res_per_bin_1lep(input_file, out_dir_base, flavour):

	model = ROOT.RDF.TH1DModel("resolution_model_hist", "resolution_model_hist", 40, -0.05, 0.05)

	if not os.path.exists(out_dir_base):
		os.mkdir(out_dir_base)

	input_rdf = get_rdf(input_file)
	input_rdf_flavor = input_rdf.Filter("n_truth_leps_from_HWW == 1").Filter("abs(pdgID_truth_leps_from_HWW[0]) == {}".format(int(flavour)))

	eta_edges = [0., 2.5, 4., 6]
	p_edges = [0., 10., 20., 30., 50., 100., 200.]

	#histogram properties based on the binning
	hist_binEdges = array("d", p_edges)
	hist_nBins = len(p_edges)-1

	list_of_hists =[]
	for i_eta_edge in range(len(eta_edges)-1):
		hist_title = "{} < |#eta| < {}".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1])
		cut_string_eta = "abs(eta_truth_leps_from_HWW[0]) > {:.2f} && abs(eta_truth_leps_from_HWW[0]) <= {:.2f}".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1])
		rdf_recomatch = input_rdf_flavor.Filter(cut_string_eta+" && n_truthmatched_leps_from_HWW_noiso == 1")
		rdf_resolution = rdf_recomatch.Define('lep_resolution', '(E_truthmatched_leps_from_HWW_noiso[0] - E_truth_leps_from_HWW[0])/E_truth_leps_from_HWW[0]')
		tmp_hist = rdf_resolution.Histo1D(model, 'lep_resolution').GetValue()   
		tmp_hist.SetTitle("{}, RMS = {:.2f}".format(hist_title, tmp_hist.GetRMS()) ) 
		gaus_pars = plot_single_hist(tmp_hist, histfilename, out_dir_base, "#sigma(E)/E", colour_code=38, file_format="png")           
		list_of_hists.append(tmp_hist)

	canvas = ROOT.TCanvas("canvas", "canvas", 800, 800) 
	canvas.cd()
	histfile_name = "{}_E_resolution.png".format(flavour)
	histfile_path = os.path.join(out_dir_base, histfile_name)

	leg = ROOT.TLegend(0.55, 0.6, 0.9, 0.9)

	for i_hist, hist in enumerate(list_of_hists):
		print("Plotting hist", i_hist)
		hist.SetLineWidth(2)
		hist.SetLineColor(38+i_hist*4)

		hist.GetYaxis().SetTitle("Fraction of events")
		hist.GetXaxis().SetTitle("Delta(E)/E")
		# hist.Draw("HIST SAME")

		hist.Scale(1./hist.Integral()) #fraction of events
		hist.SetMaximum(0.3)
		hist.Draw("HIST SAME")
		# hist.DrawNormalized("HIST SAME")

		leg.AddEntry(hist, hist.GetTitle(), "l")


	canvas.RedrawAxis()

	leg.SetFillStyle( 0 )
	leg.SetBorderSize( 0 )
	leg.SetMargin( 0.1)
	leg.SetTextFont( 43 )
	leg.SetTextSize( 20 )
	leg.SetColumnSeparation(-0.05)
	leg.Draw()

	canvas.SaveAs(histfile_path)



def check_eff_per_bin_1lep(input_rdf, out_dir_base, flavour, with_iso=False, with_larger_dR=False):
	eta_edges = [0., 2.5, 4., 6]
	pT_edges = [0., 5., 10., 15., 20., 30., 40., 60., 80., 100., 150., 200., 300.,]
	# pT_edges = [0., 10., 20., 30., 50., 100., 200.]

	#histogram properties based on the binning
	hist_binEdges = array("d", pT_edges)
	hist_nBins = len(pT_edges)-1

	list_of_hists =[]

	if with_iso and with_larger_dR:
		raiseException("Error in check_eff_per_bin_1lep - with_iso and with_larger_dR cannot be true at the same time.")

	recomatch_var = "n_truthmatched_leps_from_HWW_noiso"
	if with_iso:
		recomatch_var = "n_truthmatched_leps_from_HWW" 
	if with_larger_dR:
		recomatch_var = "n_truthmatched_leps_from_HWW_noiso_dr02"


	for i_eta_edge in range(len(eta_edges)-1):
		#write to file:
		file_name = "{}_efficiencies_vs_pT_eta_bin_{}.txt".format(flavour, i_eta_edge)
		file_path = os.path.join(out_dir_base, file_name)

		#fill a histogram
		hist_name = "hist_eff_vs_pT_eta_bin"+str(i_eta_edge)
		hist_eff_vs_pT = ROOT.TH1D(hist_name, hist_name, hist_nBins, hist_binEdges)
		hist_title = "{} < |#eta| < {}".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1])

		with open(file_path, 'w') as outfile:
			eff_vs_pT = []
			cut_string_eta = "abs(eta_truth_leps_from_HWW[0]) > {:.2f} && abs(eta_truth_leps_from_HWW[0]) <= {:.2f}".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1])
			for i_pT_edge in range(len(pT_edges)-1):
				cut_string_bin = cut_string_eta+" && pT_truth_leps_from_HWW[0] > {:.2f} && pT_truth_leps_from_HWW[0] <= {:.2f}".format(pT_edges[i_pT_edge], pT_edges[i_pT_edge+1])
				n_evts_bin_total = input_rdf.Filter(cut_string_bin).Count().GetValue()
				# n_evts_bin_total = rdf_evts_bin.Count().GetValue()
				n_evts_bin_recomatched = input_rdf.Filter(cut_string_bin+" && {} == 1".format(recomatch_var)).Count().GetValue()
				# n_evts_bin_recomatched = input_rdf.Filter(cut_string_bin+" && n_truthmatched_leps_from_HWW_noiso == 1").Count().GetValue()
				if n_evts_bin_total:
					eff_bin = n_evts_bin_recomatched/n_evts_bin_total*100.
				else:
					eff_bin = 0.
				eff_vs_pT.append(eff_bin)
				print(eff_bin)
				outfile.write("{} to {} GeV : {:.2f} \n".format(pT_edges[i_pT_edge], pT_edges[i_pT_edge+1], eff_bin))

				#fill the hist
				hist_eff_vs_pT.SetBinContent(i_pT_edge+1, eff_bin)

		hist_eff_vs_pT.SetTitle(hist_title)
		list_of_hists.append(hist_eff_vs_pT)

	if with_iso:
		histfile_name = "{}_efficiencies_vs_pT_afterIsolation.png".format(flavour)
	elif with_larger_dR:
		histfile_name = "{}_efficiencies_vs_pT_dR02.png".format(flavour)
	else:
		histfile_name = "{}_efficiencies_vs_pT.png".format(flavour)

	histfile_path = os.path.join(out_dir_base, histfile_name)
	canvas = ROOT.TCanvas("canvas", "canvas", 800, 800) 
	canvas.cd()

	leg = ROOT.TLegend(0.65, 0.2, 0.85, 0.4)

	for i_hist, hist in enumerate(list_of_hists):
		print("Plotting hist", i_hist)
		hist.SetLineWidth(2)
		hist.SetLineColor(38+i_hist*4)

		hist.SetMinimum(0.)
		hist.SetMaximum(105.)
		hist.GetYaxis().SetTitle("{} efficiency in %".format(flavour))
		hist.GetXaxis().SetTitle("p_{T} truth in GeV")
		hist.Draw("HIST SAME")

		leg.AddEntry(hist, hist.GetTitle(), "l")

	leg.SetFillStyle( 0 )
	leg.SetBorderSize( 0 )
	leg.SetTextFont( 43 )
	leg.SetTextSize( 22 )
	leg.SetColumnSeparation(-0.05)
	leg.Draw()

	canvas.SaveAs(histfile_path)

def check_eff_per_eta_bin_1lep(input_rdf, out_dir_base, flavour, with_iso=False, with_larger_dR=False):
	eta_edges = [-6., -4., -2.5, -2.0, -1.5, -1.0, -0.5, 0., 0.5, 1.0, 1.5, 2.0, 2.5, 4., 6]
	pT_edges = [0., 20., 40., 60., 80., 100., 200.]

	#histogram properties based on the binning
	hist_binEdges = array("d", eta_edges)
	hist_nBins = len(eta_edges)-1

	list_of_hists =[]

	if with_iso and with_larger_dR:
		raiseException("Error in check_eff_per_bin_1lep - with_iso and with_larger_dR cannot be true at the same time.")

	recomatch_var = "n_truthmatched_leps_from_HWW_noiso"
	if with_iso:
		recomatch_var = "n_truthmatched_leps_from_HWW" 
	if with_larger_dR:
		recomatch_var = "n_truthmatched_leps_from_HWW_noiso_dr02"


	for i_pt_edge in range(len(pT_edges)-1):
		#write to file:
		file_name = "{}_efficiencies_vs_eta_pT_bin_{}.txt".format(flavour, i_pt_edge)
		file_path = os.path.join(out_dir_base, file_name)

		#fill a histogram
		hist_name = "hist_eff_vs_eta_pT_bin"+str(i_pt_edge)
		hist_eff_vs_eta = ROOT.TH1D(hist_name, hist_name, hist_nBins, hist_binEdges)
		hist_title = "{} < p_{{T}} < {}".format(pT_edges[i_pt_edge], pT_edges[i_pt_edge+1])

		with open(file_path, 'w') as outfile:
			eff_vs_eta = []
			cut_string_pT = "pT_truth_leps_from_HWW[0] > {:.2f} && pT_truth_leps_from_HWW[0] <= {:.2f}".format(pT_edges[i_pt_edge], pT_edges[i_pt_edge+1])
			for i_eta_edge in range(len(eta_edges)-1):
				cut_string_bin = cut_string_pT+" && eta_truth_leps_from_HWW[0] > {:.2f} && eta_truth_leps_from_HWW[0] <= {:.2f}".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1])
				n_evts_bin_total = input_rdf.Filter(cut_string_bin).Count().GetValue()
				# n_evts_bin_total = rdf_evts_bin.Count().GetValue()
				n_evts_bin_recomatched = input_rdf.Filter(cut_string_bin+" && {} == 1".format(recomatch_var)).Count().GetValue()
				# n_evts_bin_recomatched = input_rdf.Filter(cut_string_bin+" && n_truthmatched_leps_from_HWW_noiso == 1").Count().GetValue()
				if n_evts_bin_total:
					eff_bin = n_evts_bin_recomatched/n_evts_bin_total*100.
				else:
					eff_bin = 0.
				eff_vs_eta.append(eff_bin)
				print(eff_bin)
				outfile.write("{} to {} GeV : {:.2f} \n".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1], eff_bin))

				#fill the hist
				hist_eff_vs_eta.SetBinContent(i_eta_edge+1, eff_bin)

		hist_eff_vs_eta.SetTitle(hist_title)
		list_of_hists.append(hist_eff_vs_eta)

	if with_iso:
		histfile_name = "{}_efficiencies_vs_eta_afterIsolation.png".format(flavour)
	elif with_larger_dR:
		histfile_name = "{}_efficiencies_vs_eta_dR02.png".format(flavour)
	else:
		histfile_name = "{}_efficiencies_vs_eta.png".format(flavour)

	histfile_path = os.path.join(out_dir_base, histfile_name)
	canvas = ROOT.TCanvas("canvas", "canvas", 800, 800) 
	canvas.cd()

	leg = ROOT.TLegend(0.6, 0.2, 0.8, 0.4)

	for i_hist, hist in enumerate(list_of_hists):
		print("Plotting hist", i_hist)
		hist.SetLineWidth(2)
		hist.SetLineColor(30+i_hist*2)

		hist.SetMinimum(0.)
		hist.SetMaximum(105.)
		hist.GetYaxis().SetTitle("{} efficiency in %".format(flavour))
		hist.GetXaxis().SetTitle("#eta truth")
		hist.Draw("HIST SAME")

		leg.AddEntry(hist, hist.GetTitle(), "l")

	leg.SetFillStyle( 0 )
	leg.SetBorderSize( 0 )
	leg.SetTextFont( 43 )
	leg.SetTextSize( 22 )
	leg.SetColumnSeparation(-0.05)
	leg.Draw()

	canvas.SaveAs(histfile_path)

def check_photon_res_per_eta_bin(input_rdf, cutstring_base, E_edges, hist_name, filebasename, out_dir_base):

	model = ROOT.RDF.TH1DModel("resolution_model_hist", "resolution_model_hist", 40, -0.05, 0.05)

	#histogram vs E
	hist_binEdges = array("d", E_edges)
	hist_nBins = len(E_edges)-1
	hist_res_vs_E = ROOT.TH1D(filebasename, filebasename, hist_nBins, hist_binEdges)

	rdf_bin = input_rdf.Filter(cutstring_base)
	#rdf_resolution = rdf_bin.Define('lep_resolution', '(E_truthmatched_ys_from_higgs_noiso[0] - E_truth_ys_from_higgs[0])/E_truth_ys_from_higgs[0]')
	rdf_resolution = rdf_bin.Define('lep_resolution', '(E_truthmatched_leps_from_HWW_noiso[0] - E_truth_leps_from_HWW[0])/E_truth_leps_from_HWW[0]')

	for i_E_edge in range(len(E_edges)-1):
		cutstring_bin = "E_truthmatched_leps_from_HWW_noiso[0] > {:.2f} && E_truthmatched_leps_from_HWW_noiso[0] <= {:.2f}".format(E_edges[i_E_edge], E_edges[i_E_edge+1])
		rdf_bin = rdf_resolution.Filter(cutstring_bin)

		#store a histogram of the resolution 
		tmp_hist = rdf_bin.Histo1D(model, 'lep_resolution').GetValue()   
		histfilename = "{}_E_{}_to_{}".format(filebasename, E_edges[i_E_edge], E_edges[i_E_edge+1])
		tmp_hist.SetTitle("{}, RMS = {:.4f}".format(hist_name, tmp_hist.GetRMS()) )     
		gaus_pars = plot_single_hist(tmp_hist, histfilename, out_dir_base, "#sigma(E)/E", colour_code=38, file_format="png")
		
		# hist_res_vs_E.SetBinContent(i_E_edge+1, tmp_hist.GetRMS())
		if gaus_pars:
			hist_res_vs_E.SetBinContent(i_E_edge+1, gaus_pars[2])
			hist_res_vs_E.SetBinError(i_E_edge+1, gaus_pars[3])

	plot_single_hist(hist_res_vs_E, filebasename, out_dir_base, "E_{true} in GeV", colour_code=38, file_format="png")
	# plot_2D(rdf_resolution, 'pT_truthmatched_ys_from_higgs_noiso', 'y_resolution', out_dir_base)	

	
	return hist_res_vs_E   


def plot_single_hist(hist, filename, out_dir_base, xaxis_label, colour_code=38, file_format="png"):

	canvas = ROOT.TCanvas("canvas", "canvas", 800, 800) 
	canvas.cd()
	histfile_name = "{}.{}".format(filename, file_format)
	histfile_path = os.path.join(out_dir_base, histfile_name)

	#fit the histogram with a gaus:
	gauss = ROOT.TF1("gauss","gaus", -1., 1.)
	hist.Fit(gauss)
	fit_result= hist.GetFunction("gauss")

	
	hist.SetLineWidth(2)
	hist.SetLineColor(colour_code)
	hist.GetYaxis().SetTitle("Events")
	hist.GetXaxis().SetTitle(xaxis_label)

	gaus_pars = []
	if fit_result: #avoid crashes from fitting empty histograms
		fit_result.SetLineColor(ROOT.kBlack)
		fit_result.SetLineWidth(2)
		fit_result.Draw()

		#get the parameter values:
		gaus_mean = fit_result.GetParameter(1)
		gaus_mean_error = fit_result.GetParError(1)
		gaus_width = fit_result.GetParameter(2)
		gaus_width_error = fit_result.GetParError(2)
		gaus_pars = [gaus_mean, gaus_mean_error, gaus_width, gaus_width_error]

	hist.Draw("HIST SAME")

	leg = ROOT.TLegend(0.55, 0.6, 0.9, 0.9)
	leg.SetFillStyle( 0 )
	leg.SetBorderSize( 0 )
	leg.SetMargin( 0.1)
	leg.SetTextFont( 43 )
	leg.SetTextSize( 20 )
	leg.SetColumnSeparation(-0.05)
	leg.AddEntry(hist, hist.GetTitle(), "l")
	leg.Draw()

	canvas.SaveAs(histfile_path)

	return gaus_pars

def plot_list_of_hists(list_of_hists, histbasename, out_dir_base, xaxis_label, yaxis_label="Events", file_format="png"):
	canvas = ROOT.TCanvas("canvas", "canvas", 800, 800) 
	canvas.cd()
	canvas.SetLeftMargin(0.15)
	histfile_name = "{}.{}".format(histbasename, file_format)
	histfile_path = os.path.join(out_dir_base, histfile_name)

	leg = ROOT.TLegend(0.55, 0.6, 0.9, 0.9)

	for i_hist, hist in enumerate(list_of_hists):
		print("Plotting hist", i_hist, "with name", hist.GetTitle() )
		hist.SetLineWidth(2)
		hist.SetLineColor(38+i_hist*4)

		hist.GetYaxis().SetTitle(yaxis_label)
		hist.GetXaxis().SetTitle(xaxis_label)
		hist.Draw("HISTE SAME")
		leg.AddEntry(hist, hist.GetTitle(), "l")


	canvas.RedrawAxis()

	leg.SetFillStyle( 0 )
	leg.SetBorderSize( 0 )
	leg.SetMargin( 0.1)
	leg.SetTextFont( 43 )
	leg.SetTextSize( 20 )
	leg.SetColumnSeparation(-0.05)
	leg.Draw()

	canvas.SaveAs(histfile_path)

def check_lepton_resolution_and_eff(input_filepath, out_dir_base):

	#how many of the 1 lepton events have 1 lepton? -> ideally link the truth particle to a reco particle!!

	#first check: 2 lepton events, how many have at least 2 leptons? no truth links 

	if not os.path.exists(out_dir_base):
		os.mkdir(out_dir_base)

	rdf = ROOT.RDataFrame("events", input_filepath)

	if not rdf:
		print("Empty file for:", input_filepath, " Exiting.")
		return

	rdf_lvqq_truth = rdf.Filter("n_truth_leps_from_HWW == 1") 

	rdf_1electron_truth = rdf_lvqq_truth.Filter("abs(pdgID_truth_leps_from_HWW[0]) == 13 ")
	rdf_lep_recomatched = rdf_1electron_truth.Filter("n_truthmatched_leps_from_HWW == 1")
	rdf_lep_recomatched_wIso = rdf_1electron_truth.Filter("n_truthmatched_leps_from_HWW_noiso == 1")
	n_1electron_truth_total = rdf_1electron_truth.Count().GetValue()
	n_evts_1electron_recomatched = rdf_1electron_truth.Filter("n_truthmatched_leps_from_HWW_noiso == 1").Count().GetValue()
	n_evts_1electron_recomatched_wIso = rdf_1electron_truth.Filter("n_truthmatched_leps_from_HWW == 1").Count().GetValue()
	print("Efficiency for 1 matched electron before iso: {:.2f}%".format(n_evts_1electron_recomatched/n_1electron_truth_total*100.))
	print("Efficiency for 1 matched electron after iso: {:.2f}%".format(n_evts_1electron_recomatched_wIso/n_1electron_truth_total*100.))

	list_of_hists =[]
	eta_edges = [0., 2.5, 4., 6]
	E_edges = [0., 10., 20., 30., 50., 100., 200.]

	#check_photon_res_per_eta_bin(rdf_1electron_truth, out_dir_base, "{}".format(lep_flav))
	#check_photon_res_per_eta_bin(rdf_1electron_truth, out_dir_base, "{}".format(lep_flav), with_iso=True)

	for i_eta_edge in range(len(eta_edges)-1):
			hist_title = "{} < |#eta| < {}".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1])
			hist_filebase = "E_resolution_eta_bin{}".format(i_eta_edge)
			cut_string_eta = "abs(eta_truth_leps_from_HWW[0]) > {:.2f} && abs(eta_truth_leps_from_HWW[0]) <= {:.2f}".format(eta_edges[i_eta_edge], eta_edges[i_eta_edge+1])
			print(cut_string_eta)
			hist_bin = check_photon_res_per_eta_bin(rdf_lep_recomatched, cut_string_eta, E_edges, hist_title, hist_filebase, out_dir_base)
			list_of_hists.append(hist_bin)

	plot_list_of_hists(list_of_hists, "lep_E_resolution", out_dir_base, "E_{truth} in GeV", "#Delta E/E", file_format="png")

	#MUONS
	#rdf_1muon_truth = rdf_lvqq_truth.Filter("abs(pdgID_truth_leps_from_HWW[0]) == 13 ")
	#n_1muon_truth_total = rdf_1muon_truth.Count().GetValue()
	#n_evts_1muon_recomatched = rdf_1muon_truth.Filter("n_truthmatched_leps_from_HWW_noiso == 1").Count().GetValue()
	#n_evts_1muon_recomatched_wIso = rdf_1muon_truth.Filter("n_truthmatched_leps_from_HWW == 1").Count().GetValue()
	#print("Efficiency for 1 matched muon before iso: {:.2f}%".format(n_evts_1muon_recomatched/n_1muon_truth_total*100.))
	#print("Efficiency for 1 matched muon after iso: {:.2f}%".format(n_evts_1muon_recomatched_wIso/n_1muon_truth_total*100.))

	# check_eff_per_bin_1lep(rdf_1muon_truth, out_dir_base, "muon")
	# check_eff_per_bin_1lep(rdf_1muon_truth, out_dir_base, "muon", with_iso=True)

	#check_res_per_bin_1lep(rdf_1muon_truth, out_dir_base, "muon")
	#check_res_per_bin_1lep(rdf_1muon_truth, out_dir_base, "muon", with_iso=True)


	# #check for weird events first
	# print("Checking lepton efficiencies for 2 lepton events")
	# rdf_lvlv_truth = rdf.Filter("n_truth_leps_from_HWW == 2")
	# weird_events = rdf_lvlv_truth.Filter("n_truth_leps_from_HWW < n_truthmatched_leps_from_HWW_noiso").Count().GetValue()
	# weird_events_iso = rdf_lvlv_truth.Filter("n_truth_leps_from_HWW < n_truthmatched_leps_from_HWW").Count().GetValue()
	# if weird_events or weird_events_iso:
	# 	print("Warning! Found more recomatched leptons than truth leptons! This shouldnt happen.")

	# #count how many of those also have 2 reco matched leptons:
	# n_evts_truth_2l = rdf_lvlv_truth.Count().GetValue()
	# n_evts_recomatched_2l_noiso = rdf_lvlv_truth.Filter("n_truthmatched_leps_from_HWW_noiso == 2").Count().GetValue()
	# n_evts_recomatched_2l_iso = rdf_lvlv_truth.Filter("n_truthmatched_leps_from_HWW == 2").Count().GetValue()
	# print(n_evts_truth_2l, n_evts_recomatched_2l_noiso, n_evts_recomatched_2l_iso)

	# print("Efficiency for 2 matched leps before iso: {:.2f}%".format(n_evts_recomatched_2l_noiso/n_evts_truth_2l*100.))
	# print("Efficiency for 2 matched leps after iso: {:.2f}%".format(n_evts_recomatched_2l_iso/n_evts_truth_2l*100.))

	# #require that the truth leptons have some pT and in eta range
	# rdf_truth_2l_selected = rdf_lvlv_truth.Filter("abs(eta_truth_leps_from_HWW[0]) < 2.5 && abs(eta_truth_leps_from_HWW[1]) < 2.5")
	# n_evts_truth_2l_selected = rdf_truth_2l_selected.Count().GetValue()
	# n_evts_truth_2l_selected_recomatched_noiso = rdf_truth_2l_selected.Filter("n_truthmatched_leps_from_HWW_noiso == 2").Count().GetValue()
	# print("Efficiency for 2 matched leps before iso, and |eta| truth < 2.5: {:.2f}%".format(n_evts_truth_2l_selected_recomatched_noiso/n_evts_truth_2l_selected*100.))




if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Plot distributions for validation of new signal files")
	parser.add_argument('--input', '-i', metavar="INPUTFILE", dest="inPath", required=True, help="Path to the input directory")
	parser.add_argument('--outdir', '-o', metavar="OUTPUTDIR", dest="outDir", required=True, help="Output directory.")
	args = parser.parse_args()

	check_lepton_resolution_and_eff(args.inPath, args.outDir)
	# check_truth_brs(args.inPath, args.outDir)
	# check_res_per_bin_1lep(args.inPath, args.outDir, 13)
	# check_res_per_bin_1lep(args.inPath, args.outDir, 11)

# python bbww_lvlv_eff_rel_check.py -i /eos/user/b/bistapf/FCChh_EvtGen/FCCAnalysis_ntuples_noIso/pwp8_pp_hh_lambda100_5f_hhbbww/chunk0.root -o ./bbww_eff_check/