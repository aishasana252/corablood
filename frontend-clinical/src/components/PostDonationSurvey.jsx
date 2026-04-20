import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2, Info } from 'lucide-react';

const PostDonationSurvey = () => {
    const { donationId, fetchState } = useWorkflowStore();
    const [survey, setSurvey] = useState({
        is_completed: false,
        comfort_during_process: 0,
        staff_satisfaction: 0,
        wait_time_satisfaction: 0,
        comments: ''
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/survey/`);
            if (res.data.success && res.data.data) {
                setSurvey(res.data.data);
            }
        } catch (e) {
            console.info("Survey not completed yet");
        } finally {
            setLoading(false);
        }
    };

    const emojis = ['😠', '☹️', '😐', '😊', '😍'];

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-2xl font-bold text-slate-900">Post-Donation Care & Survey</h3>
                    <p className="text-slate-500 text-sm">Important instructions and satisfaction feedback.</p>
                </div>
            </div>

            <div className="space-y-6">
                {/* 1. Original Instructions Box (Blue) */}
                <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6">
                    <h4 className="font-bold text-blue-900 text-lg mb-4 flex items-center gap-2">
                        <Info className="w-6 h-6" />
                        Post-Donation Instructions (تعليمات ما بعد التبرع)
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-blue-800 leading-relaxed" dir="rtl">
                        <ul className="list-disc list-inside space-y-2 font-medium">
                            <li>الرجاء شرب السوائل (ماء أو عصير) قبل مغادرة بنك الدم.</li>
                            <li>عدم مغادرة كرسي التبرع حتى يأذن لك موظف بنك الدم.</li>
                            <li>عدم التدخين لمدة ساعة بعد التبرع و عدم القيادة لمدة نصف ساعة.</li>
                            <li>الإكثار من شرب السوائل في الساعات الأربع القادمة.</li>
                            <li>عدم ممارسة الرياضة القوية بعد التبرع حتى نهاية اليوم.</li>
                        </ul>
                        <ul className="list-disc list-inside space-y-2 font-medium">
                            <li>إذا مكان إبرة التبرع بدأ ينزف، ارفع يدك وأضغط عليه.</li>
                            <li>إذا شعرت بدوار، استلقِ وارفع قدميك.</li>
                            <li>لا تعود إلى العمل الشاق أو الخطير خلال 12 ساعة.</li>
                            <li>ستعود كمية الدم إلى وضعها الطبيعي بسرعة.</li>
                            <li>يمكنك مزاولة نشاطك الطبيعي بعد فترة الراحة.</li>
                        </ul>
                    </div>
                </div>

                {/* 2. Survey Content */}
                {!survey.is_completed ? (
                    <div className="bg-amber-50 border-2 border-dashed border-amber-200 rounded-3xl p-10 text-center space-y-4">
                        <div className="w-16 h-16 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto mb-2">
                            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        </div>
                        <h4 className="text-xl font-bold text-amber-900">Survey Pending on Donor Portal</h4>
                        <p className="text-amber-700 max-w-md mx-auto text-sm">This survey will be completed from the donor portal. Once finished, the results will appear here automatically.</p>
                        <div className="text-right" dir="rtl">
                            <p className="text-amber-800 font-bold text-sm">سيتم إكمال هذا الاستبيان من بوابة المتبرع. لم يكمل المتبرع الاستبيان بعد.</p>
                        </div>
                        <div className="pt-4">
                            <button onClick={fetchData} className="px-6 py-2 bg-white text-amber-600 border border-amber-200 rounded-xl font-bold hover:bg-amber-100 transition-all flex items-center gap-2 mx-auto text-xs">
                                <Loader2 className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                                Check for Survey / تحديث الاستبيان
                            </button>
                        </div>
                        <div className="pt-6 border-t border-amber-200/50 flex justify-center">
                             <button onClick={() => fetchState()} className="px-8 py-2 bg-blue-600 text-white font-bold rounded-lg shadow-lg">Skip & Finish Workflow</button>
                        </div>
                    </div>
                ) : (
                    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-8">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-8 h-8 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center">
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                            </div>
                            <h4 className="font-bold text-emerald-900">Donor Survey Responses</h4>
                        </div>

                        {/* Rating Questions (Original Emoji Design) */}
                        {[
                            { label: '1. Comfort during process (الراحة)', key: 'comfort_during_process' },
                            { label: '2. Staff satisfaction (فريق العمل)', key: 'staff_satisfaction' },
                            { label: '3. Waiting time satisfaction (وقت الانتظار)', key: 'wait_time_satisfaction' },
                        ].map((q) => (
                            <div key={q.key}>
                                <label className="block text-sm font-bold text-slate-700 mb-3">{q.label}</label>
                                <div className="flex justify-between gap-2">
                                    {[1, 2, 3, 4, 5].map(i => (
                                        <div key={i} className={`flex-1 text-center py-2 rounded-lg border transition-all ${survey[q.key] === i ? 'bg-red-50 border-red-500 text-red-700 shadow-sm' : 'bg-slate-50 border-slate-100 text-slate-300 opacity-50'}`}>
                                            <span className="text-xl block mb-1">{emojis[i-1]}</span>
                                            <span className="text-[10px] font-bold">{i}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}

                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                             <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Donor Comments</label>
                             <p className="text-slate-800 italic text-sm">{survey.comments || 'No comments provided by donor.'}</p>
                        </div>

                        <div className="flex justify-end pt-4">
                            <button onClick={() => fetchState()} className="px-8 py-3 bg-[#0ea5e9] hover:bg-[#0284c7] text-white font-bold rounded-xl shadow-lg transition-all">
                                Continue & Complete / متابعة
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PostDonationSurvey;
