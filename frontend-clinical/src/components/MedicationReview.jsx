import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2 } from 'lucide-react';

const MedicationReview = () => {
    const { donationId, donor, fetchState } = useWorkflowStore();
    const [record, setRecord] = useState({
        is_on_medication: false,
        medications_taken_names: [],
        other_medication_notes: '',
        notes: ''
    });
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/medication/`);
            if (res.data.success && res.data.data) {
                setRecord(res.data.data);
            }
        } catch (e) {
            console.info("No medication record yet");
        } finally {
            setLoading(false);
        }
    };

    const submit = async () => {
        setSubmitting(true);
        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/medication/`, {
                notes: record.notes
            });
            if (res.data.success) {
                fetchState();
            }
        } catch (e) {
            alert(e.response?.data?.message || "Failed to save record.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-2xl font-bold text-slate-900">Medication Review</h3>
                    <p className="text-slate-500 text-sm">Document medications taken by the donor.</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={submit} className="px-6 py-2 bg-[#ef4444] hover:bg-red-600 text-white font-bold rounded-lg shadow-lg flex items-center gap-2">
                        {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Approve & Continue'}
                    </button>
                </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-6">
                <div className="flex gap-4 items-center">
                    <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center text-amber-600">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </div>
                    <div>
                        <h4 className="font-bold text-amber-900">Patient-Faced Entry</h4>
                        <p className="text-sm text-amber-700">Donors can also fill this via their portal. Check recorded items here.</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-indigo-50 border border-indigo-200 rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-6 text-indigo-900 font-bold">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04M12 2.944a11.955 11.955 0 01-8.618 3.04m0 0a11.955 11.955 0 00-3.382 8.58c0 5.89 4.778 10.667 10.667 10.667m12-10.667a11.955 11.955 0 00-3.382-8.58M12 2.944a11.954 11.954 0 00-8.618 3.04" /></svg>
                        Donor Portal Entries
                    </div>
                    
                    {record.is_on_medication ? (
                        <div className="space-y-4">
                            <div className="bg-white/60 p-4 rounded-xl border border-indigo-100">
                                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Medications Listed</span>
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {record.medications_taken_names.map(name => (
                                        <span key={name} className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold">{name}</span>
                                    ))}
                                    {record.medications_taken_names.length === 0 && <span className="text-xs text-indigo-300 italic">No specific items listed</span>}
                                </div>
                            </div>
                            <div className="bg-white/60 p-4 rounded-xl border border-indigo-100">
                                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Other Notes</span>
                                <p className="text-slate-700 mt-1 font-medium text-sm italic">{record.other_medication_notes || 'No extra notes provided'}</p>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-10 opacity-50 flex flex-col items-center">
                            <p className="text-slate-500 font-bold">Donor reported no medications.</p>
                        </div>
                    )}
                </div>

                <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm">
                    <h4 className="font-bold text-slate-800 mb-6">Internal Review</h4>
                    <label className="block text-sm font-bold text-slate-600 mb-2">Pharmacist/Nurse Comments</label>
                    <textarea 
                        value={record.notes} 
                        onChange={(e) => setRecord(prev => ({...prev, notes: e.target.value}))}
                        className="w-full h-32 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl mb-6 focus:ring-2 focus:ring-red-500" 
                        placeholder="Add review notes here..."
                    ></textarea>
                    <div className="flex gap-4">
                        <button onClick={submit} className="flex-1 py-3 bg-[#ef4444] hover:bg-red-600 text-white font-bold rounded-xl shadow-lg transition-all">Skip / Approve</button>
                        <button className="px-6 py-3 bg-rose-50 text-rose-600 font-bold rounded-xl border border-rose-100">Defer Donor</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MedicationReview;
