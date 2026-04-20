import React, { useState } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2, ShieldCheck, Lock, EyeOff, Save, CheckCircle } from 'lucide-react';

const SelfExclusion = () => {
    const { donationId, fetchState } = useWorkflowStore();
    const [choice, setChoice] = useState(null);
    const [saving, setSaving] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const handleVote = async (isSafe) => {
        setChoice(isSafe);
        setSaving(true);
        try {
            await axios.post(`/api/v2/workflow/${donationId}/step/self_exclusion/`, {
                exclude_my_blood: !isSafe
            });
            setSubmitted(true);
            await fetchState();
        } catch (err) { }
        finally { setSaving(false); }
    };

    if (submitted) {
        return (
            <div className="p-12 text-center space-y-8 animate-in zoom-in-95 duration-700">
                <div className="w-24 h-24 bg-slate-900 text-white rounded-[2.5rem] flex items-center justify-center mx-auto shadow-2xl">
                    <Lock className="w-10 h-10" />
                </div>
                <div className="space-y-2">
                    <h2 className="text-3xl font-black text-slate-900 tracking-tight">Choice Secured</h2>
                    <p className="text-slate-500 font-medium">Your response has been stored and encrypted. No further action is required on this panel.</p>
                </div>
                <div className="inline-flex items-center gap-2 px-6 py-2 bg-emerald-100 text-emerald-700 rounded-full text-xs font-black tracking-widest uppercase shadow-sm">
                    <CheckCircle className="w-4 h-4" /> Confidential Record Stored
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <div className="text-center space-y-4">
                <div className="p-4 bg-slate-100 text-slate-900 rounded-3xl w-max mx-auto shadow-inner">
                    <EyeOff className="w-8 h-8" />
                </div>
                <h2 className="text-4xl font-black text-slate-900 tracking-tight">Confidential Self-Exclusion</h2>
                <p className="text-slate-500 font-medium max-w-xl mx-auto italic">
                    "Is your blood safe for transfusion? If you have any reason to believe it might not be, please select the choice below. Your answer is completely private and will not be shared with the staff."
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <button
                    onClick={() => handleVote(true)}
                    disabled={saving}
                    className="group relative overflow-hidden bg-white border-2 border-slate-100 p-10 rounded-[3rem] text-center space-y-4 transition-all hover:border-emerald-500 hover:shadow-2xl hover:shadow-emerald-500/10 hover:-translate-y-2"
                >
                    <div className="w-16 h-16 bg-emerald-50 text-emerald-500 rounded-2xl flex items-center justify-center mx-auto transition-all group-hover:scale-110 group-hover:bg-emerald-500 group-hover:text-white">
                        <ShieldCheck className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-black text-slate-800">My Blood is Safe</h3>
                    <p className="text-sm text-slate-400 font-medium">I have no reason to believe my blood carries any infectious risk.</p>
                </button>

                <button
                    onClick={() => handleVote(false)}
                    disabled={saving}
                    className="group relative overflow-hidden bg-white border-2 border-slate-100 p-10 rounded-[3rem] text-center space-y-4 transition-all hover:border-rose-500 hover:shadow-2xl hover:shadow-rose-500/10 hover:-translate-y-2"
                >
                    <div className="w-16 h-16 bg-rose-50 text-rose-500 rounded-2xl flex items-center justify-center mx-auto transition-all group-hover:scale-110 group-hover:bg-rose-500 group-hover:text-white">
                        <AlertCircle className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-black text-slate-800">Do Not Use My Blood</h3>
                    <p className="text-sm text-slate-400 font-medium tracking-tight">I have some concerns. Please dispose of my donation discreetly after collection.</p>
                </button>
            </div>

            <div className="flex justify-center">
                <div className="flex items-center gap-3 px-6 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">
                    <Lock className="w-4 h-4 opacity-40" />
                    Military Grade Encryption Active
                </div>
            </div>
        </div>
    );
};

export default SelfExclusion;
