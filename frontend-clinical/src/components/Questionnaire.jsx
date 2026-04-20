import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2 } from 'lucide-react';

const Questionnaire = () => {
    const { donationId, donor, fetchState } = useWorkflowStore();
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [isEditable, setIsEditable] = useState(true);
    const [questionnaireData, setQuestionnaireData] = useState(null);
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);

    useEffect(() => {
        fetchQuestions();
        fetchExistingAnswers();
    }, []);

    const fetchQuestions = async () => {
        try {
            const res = await axios.get('/api/v2/questions/');
            if (res.data.success) {
                setQuestions(res.data.data || []);
            }
        } catch (e) {
            console.error("Failed to fetch questions", e);
        }
    };

    const fetchExistingAnswers = async () => {
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/questionnaire/`);
            if (res.data.success && res.data.data) {
                setQuestionnaireData(res.data.data);
                setAnswers(res.data.data.answers || {});
                setIsEditable(false);
            }
        } catch (e) {
            console.info("No questionnaire responses yet");
        }
    };

    const handleAnswer = (qid, val) => {
        if (!isEditable) return;
        setAnswers(prev => ({ ...prev, [qid]: val }));
    };

    const passAll = () => {
        const passSet = {};
        questions.forEach(q => {
            passSet[q.id] = q.defer_if_answer_is === 'Yes' ? 'No' : 'Yes';
        });
        setAnswers(passSet);
    };

    const initCanvas = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.strokeStyle = '#000';
    };

    const startDrawing = (e) => {
        setIsDrawing(true);
        draw(e);
    };

    const stopDrawing = () => {
        setIsDrawing(false);
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.beginPath();
    };

    const draw = (e) => {
        if (!isDrawing) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const rect = canvas.getBoundingClientRect();
        
        let clientX, clientY;
        if (e.touches) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else {
            clientX = e.clientX;
            clientY = e.clientY;
        }

        const x = clientX - rect.left;
        const y = clientY - rect.top;

        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y);
    };

    const clearCanvas = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    const submit = async () => {
        const missing = questions.find(q => !answers[q.id]);
        if (missing) {
            alert("Please answer all questions.");
            return;
        }

        setSubmitting(true);
        try {
            const canvas = canvasRef.current;
            const signatureData = canvas ? canvas.toDataURL() : "";

            const res = await axios.post(`/api/v2/workflow/${donationId}/step/questionnaire/`, {
                answers: answers,
                signature_data: signatureData.length > 500 ? signatureData : ""
            });

            if (res.data.success) {
                fetchState();
            }
        } catch (e) {
            alert(e.response?.data?.message || "Failed to submit questions.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* QR Code Header (Original UI) */}
            <div className="flex justify-center mb-8 border-b border-slate-100 pb-6">
                <div className="flex flex-col items-center cursor-pointer group">
                    <div className="flex items-center gap-2 text-slate-700 font-bold mb-2 group-hover:text-brand-600 transition-colors">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Load Questionnaire QR Code</span>
                    </div>
                    <div className="w-32 h-32 bg-white border-2 border-slate-200 rounded-xl flex items-center justify-center shadow-sm group-hover:border-brand-500 transition-all">
                        <svg className="w-16 h-16 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v1m6 11h2m-6 0h-2v4h2v-4zM5 14v4h4v-4H5zM15 5h4v4h-4V5zM5 5h4v4H5V5z" />
                        </svg>
                    </div>
                </div>
            </div>

            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-2xl font-bold text-slate-900">Donor Questionnaire</h3>
                    <p className="text-slate-500">Mandatory health screening questions.</p>
                </div>
                <div className="flex gap-2">
                    {!isEditable && (
                        <button onClick={() => setIsEditable(true)} className="px-4 py-2 bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 font-bold rounded-lg tracking-tight">Edit Answers</button>
                    )}
                    {isEditable && (
                        <button onClick={passAll} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg flex items-center gap-2 shadow-md">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                            Pass All
                        </button>
                    )}
                </div>
            </div>

            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 mb-8 scroller-hidden">
                {questions.map((q) => (
                    <div key={q.id} className="p-4 bg-slate-50 rounded-xl border border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex-1 text-right" dir="rtl">
                            <div className="flex items-center justify-end gap-2 mb-1">
                                <span className="font-bold text-slate-900 leading-tight">{q.text_ar}</span>
                                <span className="text-xs font-mono text-slate-400">#{q.id}</span>
                            </div>
                            <p className="text-xs text-slate-500 text-left" dir="ltr">{q.text_en}</p>
                        </div>
                        <div className="flex gap-4">
                            <label className={`flex items-center gap-2 cursor-pointer p-2 rounded-lg transition-all ${answers[q.id] === 'Yes' ? 'bg-red-100 ring-1 ring-red-400' : 'bg-white border hover:border-slate-300'}`}>
                                <input type="radio" value="Yes" checked={answers[q.id] === 'Yes'} onChange={() => handleAnswer(q.id, 'Yes')} disabled={!isEditable} className="w-4 h-4 text-brand-600 disabled:opacity-50" />
                                <span className={`text-sm font-bold ${answers[q.id] === 'Yes' ? 'text-red-800' : 'text-slate-600'}`}>YES</span>
                            </label>
                            <label className={`flex items-center gap-2 cursor-pointer p-2 rounded-lg transition-all ${answers[q.id] === 'No' ? 'bg-green-100 ring-1 ring-green-400' : 'bg-white border hover:border-slate-300'}`}>
                                <input type="radio" value="No" checked={answers[q.id] === 'No'} onChange={() => handleAnswer(q.id, 'No')} disabled={!isEditable} className="w-4 h-4 text-green-600 disabled:opacity-50" />
                                <span className={`text-sm font-bold ${answers[q.id] === 'No' ? 'text-green-800' : 'text-slate-600'}`}>NO</span>
                            </label>
                        </div>
                    </div>
                ))}
            </div>

            <div className="border-t border-slate-200 pt-6 space-y-6">
                <div>
                    <label className="block text-right text-sm font-bold text-slate-700 mb-2">أسئلة إضافية أو أسباب أخرى لرفض التبرع (Other Questions)</label>
                    <textarea readOnly={!isEditable} className="w-full h-24 p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-brand-500 text-right" placeholder="..."></textarea>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-right" dir="rtl">
                    <p className="text-xs md:text-sm text-slate-800 leading-relaxed font-medium">أقر أنا الموقع أدناه بأنني قرأت وفهمت جميع بنود النشرة التثقيفية و أجبت على الأسئلة الموجهه لي في هذه الوثيقة بصدق و أن تبرعت بوحدة دم كاملة و أنا على علم بأن دمي سيستخدم في علاج المرضى و أنا على علم بأن دمي لن يستخدم في حال تبين وجود أي أمراض معدية...</p>
                </div>

                {isEditable ? (
                    <div className="flex flex-col items-end">
                        <label className="text-sm font-bold text-slate-700 mb-2">توقيع المتبرع (Signature)</label>
                        <div className="relative w-full md:w-96 h-40 bg-white border-2 border-dashed border-slate-300 rounded-xl overflow-hidden hover:border-blue-400 transition-colors">
                            <canvas 
                                ref={canvasRef} 
                                onMouseDown={startDrawing} onMouseMove={draw} onMouseUp={stopDrawing} onMouseLeave={stopDrawing}
                                onTouchStart={(e) => startDrawing(e)} onTouchMove={(e) => draw(e)} onTouchEnd={stopDrawing}
                                width={384} height={160}
                                className="w-full h-full cursor-crosshair touch-none"
                            ></canvas>
                            <button onClick={clearCanvas} className="absolute bottom-2 left-2 px-3 py-1 bg-rose-50 text-rose-600 text-xs font-bold rounded-lg border border-rose-100">Clear / مسح</button>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-end gap-3">
                         <span className="text-xs font-bold text-sky-600 uppercase tracking-widest">Verified Signature</span>
                         <div className="bg-white border-2 border-slate-200 rounded-xl p-4 w-full md:w-96 flex justify-center shadow-inner">
                            {questionnaireData?.signature_data ? (
                                <img src={questionnaireData.signature_data} alt="Signature" className="max-h-32 object-contain" />
                            ) : (
                                <span className="text-slate-300 italic text-sm">No signature available</span>
                            )}
                         </div>
                    </div>
                )}

                <div className="flex justify-between items-center pt-4 border-t border-slate-100">
                    <button className="px-6 py-2 bg-slate-100 text-slate-600 font-bold rounded-lg hover:bg-slate-200">Back / رجوع</button>
                    {isEditable ? (
                        <button onClick={submit} disabled={submitting} className="px-8 py-2 bg-[#0ea5e9] hover:bg-[#0284c7] text-white font-bold rounded-lg shadow-lg flex items-center gap-2">
                            {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                            Save Answers / حفظ وإرسال
                        </button>
                    ) : (
                        <button className="px-8 py-2 bg-emerald-50 text-emerald-600 border border-emerald-200 font-bold rounded-lg flex items-center gap-2">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                            Verified by Donor
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Questionnaire;
