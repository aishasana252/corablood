import React from 'react';
import { useWorkflowStore } from '../store/workflowStore';
import { ShieldAlert, Calendar, UserX, AlertCircle } from 'lucide-react';

const DeferralInfo = () => {
    const { donor } = useWorkflowStore();

    return (
        <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in zoom-in-95 duration-700">
            <div className="p-10 bg-rose-50 border border-rose-100 rounded-[3rem] text-center space-y-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-12 opacity-5">
                    <ShieldAlert className="w-64 h-64 text-rose-600" />
                </div>
                
                <div className="w-20 h-20 bg-white rounded-3xl shadow-xl flex items-center justify-center mx-auto text-rose-600 border border-rose-100 relative">
                    <UserX className="w-10 h-10" />
                </div>

                <div className="relative">
                    <h2 className="text-3xl font-black text-rose-900 tracking-tight">Donor Deferred</h2>
                    <p className="text-rose-700 font-medium mt-2">This donor is currently ineligible for donation based on clinical findings.</p>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-6">
                    <div className="bg-white p-4 rounded-2xl border border-rose-200">
                        <p className="text-[10px] font-black text-rose-300 uppercase tracking-widest mb-1">Reason Group</p>
                        <p className="font-bold text-rose-800">Medical Deferral</p>
                    </div>
                    <div className="bg-white p-4 rounded-2xl border border-rose-200">
                        <p className="text-[10px] font-black text-rose-300 uppercase tracking-widest mb-1">Status</p>
                        <p className="font-bold text-rose-800">Permanent</p>
                    </div>
                </div>

                <div className="p-6 bg-rose-600 text-white rounded-[2rem] shadow-2xl shadow-rose-600/20">
                    <div className="flex items-center gap-3 justify-center mb-2">
                        <Calendar className="w-5 h-5" />
                        <span className="font-black text-sm uppercase tracking-widest">Re-Entry Date</span>
                    </div>
                    <p className="text-3xl font-black tracking-tighter">NEVER / PERMANENT</p>
                </div>

                <div className="flex items-start gap-3 p-4 bg-white/50 rounded-2xl text-rose-600 text-left">
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <p className="text-xs font-bold leading-relaxed italic">
                        Please provide the donor with the official deferral letter and explain the clinical reasons for rejection. Notify the medical director if this was a false positive.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default DeferralInfo;
