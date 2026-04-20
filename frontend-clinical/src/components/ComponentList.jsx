import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2, Box, BadgeCheck, Clock, Calendar } from 'lucide-react';

const ComponentList = () => {
    const { donationId } = useWorkflowStore();
    const [components, setComponents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchComponents = async () => {
            try {
                const response = await axios.get(`/api/v2/workflow/${donationId}/step/components/`);
                if (response.data.success) {
                    setComponents(response.data.data);
                }
            } catch (err) { }
            finally { setLoading(false); }
        };
        fetchComponents();
    }, [donationId]);

    if (loading) return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-slate-400" /></div>;

    if (components.length === 0) {
        return (
            <div className="p-20 text-center bg-slate-50 border-2 border-dashed border-slate-200 rounded-[3rem]">
                <Box className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-slate-800">No Components Processed</h3>
                <p className="text-sm text-slate-500 mt-2">Blood components will be listed here once the unit is processed in the separation lab.</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center border-b border-slate-100 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-rose-50 text-rose-600 rounded-2xl">
                        <Box className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold font-display text-slate-900 tracking-tight">Derived Blood Components</h2>
                        <p className="text-sm text-slate-500 mt-1">Inventory units created from this donation</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {components.map((comp) => (
                    <div key={comp.id} className="bg-white border border-slate-200 rounded-[2.5rem] p-8 shadow-sm hover:shadow-xl transition-all border-l-8 border-l-rose-500">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <span className="px-3 py-1 bg-slate-900 text-white rounded-lg text-[10px] font-black uppercase tracking-widest">{comp.component_type}</span>
                                <h3 className="mt-2 text-2xl font-black text-slate-900 tracking-tighter">{comp.unit_number}</h3>
                            </div>
                            <div className="text-right">
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Volume</p>
                                <p className="text-xl font-black text-slate-800">{comp.volume} <span className="text-xs text-slate-400">ml</span></p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-6 border-t border-slate-100 mt-auto">
                            <div className="flex items-center gap-2 text-slate-500">
                                <Calendar className="w-4 h-4" />
                                <div className="min-w-0">
                                    <p className="text-[8px] font-black uppercase text-slate-400 tracking-widest">Expires</p>
                                    <p className="text-xs font-bold truncate">{new Date(comp.expiration_date).toLocaleDateString()}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 text-slate-500">
                                <BadgeCheck className="w-4 h-4 text-emerald-500" />
                                <div className="min-w-0">
                                    <p className="text-[8px] font-black uppercase text-slate-400 tracking-widest">Status</p>
                                    <p className="text-xs font-bold uppercase text-emerald-600 tracking-tight">{comp.status}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ComponentList;
