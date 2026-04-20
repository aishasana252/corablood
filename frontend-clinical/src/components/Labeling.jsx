import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2 } from 'lucide-react';

const Labeling = () => {
    const { donationId, donor, fetchState } = useWorkflowStore();
    const [components, setComponents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const donationCode = `WF-${donationId?.toString().padStart(5, '0')}`;

    useEffect(() => {
        fetchComponents();
    }, []);

    const fetchComponents = async () => {
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/components/`);
            if (res.data.success) {
                setComponents(res.data.data.components || []);
            }
        } catch (e) {
            console.error("Failed to fetch components", e);
        }
    };

    const printComponentLabel = async (compId) => {
        try {
            await axios.post(`/api/components/${compId}/print_label/`);
            fetchComponents();
        } catch (e) {
            alert("Print failed: " + e.message);
        }
    };

    const completeLabeling = async () => {
        setLoading(true);
        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/label/`, {});
            if (res.data.success) {
                setTimeout(() => fetchState(), 1000);
            }
        } catch (err) {
            alert('Error: ' + (err.response?.data?.message || 'Could not complete labeling'));
        } finally {
            setLoading(false);
        }
    };

    const areAllLabeled = components.length > 0 && components.every(c => c.is_labeled);

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Original Donation Code Banner */}
            <div className="mb-6 bg-slate-50 p-3 rounded-lg border border-slate-200 flex justify-center items-center gap-6 text-sm font-medium text-slate-700">
                <div className="flex items-center gap-2">
                    <span className="text-slate-500">Donation Code:</span>
                    <span className="font-bold text-red-600 text-lg font-mono">{donationCode}</span>
                </div>
            </div>

            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">Labeling</h2>
                    <p className="text-slate-500 text-sm">Print and affix initial verification labels to blood bags.</p>
                </div>
                <div className="flex gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${areAllLabeled ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                        {areAllLabeled ? 'Ready for Storage' : 'Pending Labels'}
                    </span>
                </div>
            </div>

            {/* Components Cards (Original HTML/CSS) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {components.map((comp) => (
                    <div key={comp.id} className={`p-4 bg-white border rounded-xl shadow-sm transition-all ${comp.is_labeled ? 'border-green-200 bg-green-50' : 'border-slate-200'}`}>
                        <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-xs ${comp.is_labeled ? 'bg-green-200 text-green-800' : 'bg-slate-100 text-slate-500'}`}>
                                    <span>{comp.component_type}</span>
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-slate-900 tracking-tight">{comp.unit_number || 'UNIT-01'}</p>
                                    <p className="text-xs text-slate-500 italic">{comp.volume} ml</p>
                                </div>
                            </div>
                            {comp.is_labeled && (
                                <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                </svg>
                            )}
                        </div>

                        <div className="flex justify-between items-center mt-4 border-t pt-3 border-slate-100">
                            <span className="text-xs font-mono text-slate-400">
                                {comp.is_labeled ? 'Labeled' : 'Not Labeled'}
                            </span>
                            <button 
                                onClick={() => printComponentLabel(comp.id)}
                                className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-colors flex items-center gap-2 ${comp.is_labeled ? 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50' : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow'}`}
                            >
                                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 00-2 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                                </svg>
                                {comp.is_labeled ? 'Reprint' : 'Print Label'}
                            </button>
                        </div>
                    </div>
                ))}
                {components.length === 0 && (
                    <div className="col-span-2 text-center py-10 text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                        No components found. Please complete separation first.
                    </div>
                )}
            </div>

            {/* Actions (Original Layout) */}
            <div className="flex justify-end pt-6 border-t border-slate-100">
                <button 
                    onClick={completeLabeling}
                    disabled={!areAllLabeled || components.length === 0 || loading}
                    style={{backgroundColor: '#E11D48'}}
                    className="px-6 py-3 text-white font-bold rounded-xl shadow-lg hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5 flex items-center gap-2"
                >
                    {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                    Complete & Move to Storage
                </button>
            </div>
        </div>
    );
};

export default Labeling;
