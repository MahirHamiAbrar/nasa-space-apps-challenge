import React, { useState, useMemo } from 'react';
import { Upload, Search, Filter, Download, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const ExoplanetDashboard = () => {
  const [inputData, setInputData] = useState([]);
  const [predictionsData, setPredictionsData] = useState([]);
  const [actualData, setActualData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [confidenceFilter, setConfidenceFilter] = useState(0);
  const [dispositionFilter, setDispositionFilter] = useState('ALL');
  const [selectedPlanet, setSelectedPlanet] = useState(null);

  const parseCSV = (text) => {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    return lines.slice(1).map(line => {
      const values = line.split(',');
      const obj = {};
      headers.forEach((header, i) => {
        obj[header] = values[i]?.trim() || '';
      });
      return obj;
    });
  };

  const handleFileUpload = (e, setData) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const parsed = parseCSV(event.target.result);
        setData(parsed);
      };
      reader.readAsText(file);
    }
  };

  const mergedData = useMemo(() => {
    if (!inputData.length || !predictionsData.length) return [];
    
    return inputData.map(input => {
      const prediction = predictionsData.find(p => p.object_name === input.object_name);
      const actual = actualData.find(a => a.object_name === input.object_name);
      
      return {
        ...input,
        predicted_probability: prediction?.predicted_probability || 'N/A',
        lgb_prediction: prediction?.lgb_prediction || 'N/A',
        actual_disposition: actual?.disposition || input.disposition
      };
    });
  }, [inputData, predictionsData, actualData]);

  const filteredData = useMemo(() => {
    return mergedData.filter(planet => {
      const matchesSearch = planet.object_name.toLowerCase().includes(searchTerm.toLowerCase());
      const probability = parseFloat(planet.predicted_probability);
      const matchesConfidence = isNaN(probability) || probability >= confidenceFilter;
      const matchesDisposition = dispositionFilter === 'ALL' || planet.actual_disposition === dispositionFilter;
      
      return matchesSearch && matchesConfidence && matchesDisposition;
    });
  }, [mergedData, searchTerm, confidenceFilter, dispositionFilter]);

  const statistics = useMemo(() => {
    if (!mergedData.length) return { total: 0, confirmed: 0, falsePositives: 0, candidates: 0, accuracy: 0 };
    
    const confirmed = mergedData.filter(p => p.actual_disposition === 'CONFIRMED').length;
    const falsePositives = mergedData.filter(p => p.actual_disposition === 'FALSE POSITIVE').length;
    const candidates = mergedData.filter(p => p.actual_disposition === 'CANDIDATE').length;
    
    const withPredictions = mergedData.filter(p => p.lgb_prediction !== 'N/A');
    const correct = withPredictions.filter(p => {
      const isConfirmed = p.actual_disposition === 'CONFIRMED';
      const predicted = p.lgb_prediction === '1';
      return (isConfirmed && predicted) || (!isConfirmed && !predicted);
    }).length;
    
    const accuracy = withPredictions.length > 0 ? (correct / withPredictions.length * 100).toFixed(1) : 0;
    
    return {
      total: mergedData.length,
      confirmed,
      falsePositives,
      candidates,
      accuracy
    };
  }, [mergedData]);

  const exportToCSV = () => {
    if (!filteredData.length) return;
    
    const headers = Object.keys(filteredData[0]).join(',');
    const rows = filteredData.map(row => Object.values(row).join(','));
    const csv = [headers, ...rows].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'exoplanet_results.csv';
    a.click();
  };

  const getDispositionIcon = (disposition) => {
    if (disposition === 'CONFIRMED') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (disposition === 'FALSE POSITIVE') return <XCircle className="w-5 h-5 text-red-500" />;
    return <AlertCircle className="w-5 h-5 text-yellow-500" />;
  };

  const getConfidenceColor = (probability) => {
    const prob = parseFloat(probability);
    if (isNaN(prob)) return 'bg-gray-200';
    if (prob >= 0.9) return 'bg-green-500';
    if (prob >= 0.7) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Exoplanet Detection Dashboard
          </h1>
          <p className="text-gray-400">NASA Space Apps Challenge - ML Pipeline for Transit Detection <strong><sub>by Exosphere</sub></strong></p>
        </div>

        {/* File Upload Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <label className="flex flex-col items-center cursor-pointer">
              <Upload className="w-8 h-8 text-blue-400 mb-2" />
              <span className="text-sm font-medium mb-2">Upload Input Data</span>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => handleFileUpload(e, setInputData)}
                className="hidden"
              />
              <span className="text-xs text-gray-400">
                {inputData.length > 0 ? `${inputData.length} records loaded` : 'No file selected'}
              </span>
            </label>
          </div>

          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <label className="flex flex-col items-center cursor-pointer">
              <Upload className="w-8 h-8 text-purple-400 mb-2" />
              <span className="text-sm font-medium mb-2">Upload Predictions</span>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => handleFileUpload(e, setPredictionsData)}
                className="hidden"
              />
              <span className="text-xs text-gray-400">
                {predictionsData.length > 0 ? `${predictionsData.length} predictions loaded` : 'No file selected'}
              </span>
            </label>
          </div>

          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <label className="flex flex-col items-center cursor-pointer">
              <Upload className="w-8 h-8 text-green-400 mb-2" />
              <span className="text-sm font-medium mb-2">Upload Actual Results</span>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => handleFileUpload(e, setActualData)}
                className="hidden"
              />
              <span className="text-xs text-gray-400">
                {actualData.length > 0 ? `${actualData.length} records loaded` : 'Optional'}
              </span>
            </label>
          </div>
        </div>

        {/* Statistics Cards */}
        {mergedData.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="text-2xl font-bold text-blue-400">{statistics.total}</div>
              <div className="text-sm text-gray-400">Total Candidates</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="text-2xl font-bold text-green-400">{statistics.confirmed}</div>
              <div className="text-sm text-gray-400">Confirmed</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="text-2xl font-bold text-red-400">{statistics.falsePositives}</div>
              <div className="text-sm text-gray-400">False Positives</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="text-2xl font-bold text-yellow-400">{statistics.candidates}</div>
              <div className="text-sm text-gray-400">Candidates</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="text-2xl font-bold text-purple-400">{statistics.accuracy}%</div>
              <div className="text-sm text-gray-400">ML Accuracy</div>
            </div>
          </div>
        )}

        {/* Filters */}
        {mergedData.length > 0 && (
          <div className="bg-slate-800 rounded-lg p-4 mb-6 border border-slate-700">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <Search className="w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by object name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="flex-1 bg-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={dispositionFilter}
                  onChange={(e) => setDispositionFilter(e.target.value)}
                  className="flex-1 bg-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ALL">All Dispositions</option>
                  <option value="CONFIRMED">Confirmed</option>
                  <option value="FALSE POSITIVE">False Positive</option>
                  <option value="CANDIDATE">Candidate</option>
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs text-gray-400">Min Confidence: {confidenceFilter.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={confidenceFilter}
                  onChange={(e) => setConfidenceFilter(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <button
                onClick={exportToCSV}
                className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 rounded px-4 py-2 text-sm font-medium transition"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          </div>
        )}

        {/* Planet Cards */}
        {mergedData.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredData.map((planet, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedPlanet(planet)}
                className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-blue-500 cursor-pointer transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-blue-400">{planet.object_name}</h3>
                    <p className="text-xs text-gray-400">{planet.mission}</p>
                  </div>
                  {getDispositionIcon(planet.actual_disposition)}
                </div>

                <div className="space-y-2 mb-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Disposition:</span>
                    <span className="font-medium">{planet.actual_disposition}</span>
                  </div>
                  {planet.predicted_probability !== 'N/A' && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Confidence:</span>
                      <span className="font-medium">{(parseFloat(planet.predicted_probability) * 100).toFixed(1)}%</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Period:</span>
                    <span className="font-medium">{parseFloat(planet.period).toFixed(2)} days</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Planet Radius:</span>
                    <span className="font-medium">{planet.planet_radius} R⊕</span>
                  </div>
                </div>

                {planet.predicted_probability !== 'N/A' && (
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getConfidenceColor(planet.predicted_probability)}`}
                      style={{ width: `${parseFloat(planet.predicted_probability) * 100}%` }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-slate-800 rounded-lg p-12 text-center border border-slate-700">
            <Upload className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">No Data Loaded</h3>
            <p className="text-gray-500">Upload your CSV files to get started</p>
          </div>
        )}

        {/* Detail Modal */}
        {selectedPlanet && (
          <div
            onClick={() => setSelectedPlanet(null)}
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-700"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-blue-400">{selectedPlanet.object_name}</h2>
                  <p className="text-gray-400">Detailed Information</p>
                </div>
                <button
                  onClick={() => setSelectedPlanet(null)}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Mission</div>
                  <div className="font-medium">{selectedPlanet.mission}</div>
                </div>
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Disposition</div>
                  <div className="font-medium">{selectedPlanet.actual_disposition}</div>
                </div>
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Orbital Period</div>
                  <div className="font-medium">{parseFloat(selectedPlanet.period).toFixed(2)} days</div>
                </div>
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Planet Radius</div>
                  <div className="font-medium">{selectedPlanet.planet_radius} R⊕</div>
                </div>
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Star Temperature</div>
                  <div className="font-medium">{selectedPlanet.star_temp} K</div>
                </div>
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Star Radius</div>
                  <div className="font-medium">{selectedPlanet.star_radius} R☉</div>
                </div>
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Star Mass</div>
                  <div className="font-medium">{selectedPlanet.star_mass} M☉</div>
                </div>
                <div className="bg-slate-700 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Discovery Facility</div>
                  <div className="font-medium">{selectedPlanet.discovery_facility}</div>
                </div>
                {selectedPlanet.predicted_probability !== 'N/A' && (
                  <>
                    <div className="bg-slate-700 rounded p-3">
                      <div className="text-xs text-gray-400 mb-1">ML Confidence</div>
                      <div className="font-medium">{(parseFloat(selectedPlanet.predicted_probability) * 100).toFixed(2)}%</div>
                    </div>
                    <div className="bg-slate-700 rounded p-3">
                      <div className="text-xs text-gray-400 mb-1">ML Prediction</div>
                      <div className="font-medium">{selectedPlanet.lgb_prediction === '1' ? 'Positive' : 'Negative'}</div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExoplanetDashboard;
