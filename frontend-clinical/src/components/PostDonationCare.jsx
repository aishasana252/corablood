import React, { useState } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2 } from 'lucide-react';

const PostDonationCare = () => {
    const { donationId, fetchState } = useWorkflowStore();
    const [submitting, setSubmitting] = useState(false);

    const submit = async () => {
        setSubmitting(true);
        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/post_donation/`, {});
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
                    <h3 className="text-2xl font-bold text-slate-900">Post-Donation Care</h3>
                    <p className="text-slate-500 text-sm">Record verification of donor recovery and rest period.</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={submit} disabled={submitting} className="px-6 py-2 bg-[#ef4444] hover:bg-red-600 text-white font-bold rounded-lg shadow-lg flex items-center gap-2 transition-all">
                        {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                        Complete Rest Period
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                    <label className="flex items-center gap-3 p-4 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer hover:bg-white transition-colors">
                        <input type="checkbox" defaultChecked className="w-5 h-5 text-red-600 rounded" />
                        <span className="font-bold text-slate-700 text-sm">Donor remained in rest area for 15 mins?</span>
                    </label>
                    <label className="flex items-center gap-3 p-4 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer hover:bg-white transition-colors">
                        <input type="checkbox" defaultChecked className="w-5 h-5 text-red-600 rounded" />
                        <span className="font-bold text-slate-700 text-sm">Donor had post-donation snacks?</span>
                    </label>
                    <label className="flex items-center gap-3 p-4 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer hover:bg-white transition-colors">
                        <input type="checkbox" defaultChecked className="w-5 h-5 text-red-600 rounded" />
                        <span className="font-bold text-slate-700 text-sm">No immediate reactions observed?</span>
                    </label>
                </div>
                
                <div className="bg-indigo-50 p-6 rounded-2xl border border-indigo-100">
                    <h4 className="font-bold text-indigo-900 mb-4 text-center uppercase tracking-widest text-xs">Protocol Reminder</h4>
                    <ul className="text-sm text-indigo-700 list-disc list-inside space-y-3 font-medium">
                        <li>Ensure site is not bleeding.</li>
                        <li>Advise donor to drink plenty of fluids.</li>
                        <li>Advise avoiding heavy lifting for 24 hours.</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default PostDonationCare;
