import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useDonorStore } from '../store/donorStore';
import { Loader2, CheckCircle, Save, ChevronRight, ChevronLeft, ShieldCheck, HelpCircle } from 'lucide-react';

const Questionnaire = () => {
    const { fetchState } = useDonorStore();
    const [questions, setQuestions] = useState({});
    const [loading, setLoading] = useState(true);
    const [answers, setAnswers] = useState({});
    const [currentCategoryIdx, setCurrentCategoryIdx] = useState(0);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const fetchQuestions = async () => {
            try {
                const res = await axios.get('/portal/api/questions/');
                if (res.data.success) {
                    setQuestions(res.data.data);
                }
            } catch (err) {}
            finally { setLoading(false); }
        };
        fetchQuestions();
    }, []);

    const categories = Object.keys(questions);
    const currentCategory = categories[currentCategoryIdx];
    const categoryQuestions = questions[currentCategory] || [];

    const handleAnswer = (qId, val) => {
        setAnswers({ ...answers, [qId]: val });
    };

    const isCategoryComplete = () => {
        return categoryQuestions.every(q => answers[q.id] !== undefined);
    };

    const handleNext = () => {
        if (currentCategoryIdx < categories.length - 1) {
            setCurrentCategoryIdx(currentCategoryIdx + 1);
            window.scrollTo(0, 0);
        } else {
            handleSubmit();
        }
    };

    const handleSubmit = async () => {
        setSaving(true);
        try {
            const res = await axios.post('/portal/api/submit/questionnaire/', { 
                answers,
                signature_data: "Digitally Signed by Donor" // Placeholder for actual sign
            });
            if (res.data.success) {
                await fetchState();
            }
        } catch (err) {}
        finally { setSaving(false); }
    };

    if (loading) return <div className="flex justify-center p-12"><Loader2 className="w-12 h-12 animate-spin text-brand-500" /></div>;

    return (
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 sm:p-12 shadow-xl shadow-brand-900/10 border border-white/50 space-y-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-brand-100 to-transparent rounded-full blur-[60px] pointer-events-none"></div>

            <div className="space-y-2 border-b border-slate-100 pb-6 relative z-10">
                <div className="flex items-center gap-2 text-rose-500">
                    <HelpCircle className="w-6 h-6" />
                    <span className="text-sm font-bold uppercase tracking-widest bg-rose-100 text-rose-600 px-3 py-1 rounded-full">Medical Screening</span>
                </div>
                <h2 className="text-3xl font-display font-bold text-slate-800 tracking-tight mt-4">{currentCategory}</h2>
                <p className="text-slate-500 text-base">Please answer all questions honestly for your safety and the patient's.</p>
            </div>

            <div className="grid grid-cols-1 gap-6 relative z-10">
                {categoryQuestions.map((q) => (
                    <div key={q.id} className="p-8 bg-white/60 backdrop-blur-md rounded-[2rem] border border-white/50 shadow-lg shadow-brand-900/5 space-y-6 hover:-translate-y-1 hover:shadow-brand-900/10 transition-all duration-300">
                        <div className="flex gap-4">
                            <span className="w-10 h-10 rounded-2xl bg-gradient-to-br from-brand-100 to-rose-50 flex items-center justify-center text-sm font-bold text-brand-600 shadow-inner">?</span>
                            <div className="flex-1 space-y-2">
                                <h4 className="text-lg font-bold text-slate-800 leading-snug">{q.text}</h4>
                                <h4 className="text-slate-400 text-md font-arabic text-left" dir="ltr">{q.text_ar}</h4>
                            </div>
                        </div>

                        <div className="flex gap-4 pt-2">
                            <button
                                onClick={() => handleAnswer(q.id, 'yes')}
                                className={`flex-1 py-4 rounded-xl font-bold text-sm sm:text-base transition-all border-2 shadow-sm ${
                                    answers[q.id] === 'yes' 
                                    ? 'bg-brand-50 border-brand-500 text-brand-600 shadow-brand-200' 
                                    : 'bg-white border-slate-100 text-slate-400 hover:border-brand-200 hover:text-brand-500'
                                }`}
                            >
                                YES / نعم
                            </button>
                            <button
                                onClick={() => handleAnswer(q.id, 'no')}
                                className={`flex-1 py-4 rounded-xl font-bold text-sm sm:text-base transition-all border-2 shadow-sm ${
                                    answers[q.id] === 'no' 
                                    ? 'bg-emerald-50 border-emerald-500 text-emerald-600 shadow-emerald-200' 
                                    : 'bg-white border-slate-100 text-slate-400 hover:border-emerald-200 hover:text-emerald-500'
                                }`}
                            >
                                NO / لا
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex flex-col-reverse sm:flex-row items-center justify-between pt-8 border-t border-slate-100 gap-4 relative z-10">
                <button
                    disabled={currentCategoryIdx === 0}
                    onClick={() => setCurrentCategoryIdx(currentCategoryIdx - 1)}
                    className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-2xl font-bold text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-all disabled:opacity-0"
                >
                    <ChevronLeft className="w-5 h-5" /> Previous
                </button>
                
                <div className="flex items-center gap-6 w-full sm:w-auto">
                    <p className="text-xs font-bold text-slate-400 uppercase hidden md:block tracking-widest">
                        Section {currentCategoryIdx + 1} / {categories.length}
                    </p>
                    <button
                        disabled={!isCategoryComplete() || saving}
                        onClick={handleNext}
                        className={`w-full sm:w-auto flex justify-center items-center gap-3 px-10 py-4 rounded-2xl font-bold text-lg transition-all shadow-xl ${
                            isCategoryComplete() 
                            ? 'bg-slate-900 text-white hover:bg-brand-600 hover:scale-105 hover:shadow-brand-500/30' 
                            : 'bg-slate-100 text-slate-300 cursor-not-allowed shadow-none'
                        }`}
                    >
                        {saving ? <Loader2 className="w-6 h-6 animate-spin" /> : (
                            currentCategoryIdx === categories.length - 1 ? 'Finish & Sign' : 'Continue'
                        )}
                        <ChevronRight className="w-6 h-6" />
                    </button>
                </div>
            </div>

            <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100/50 rounded-2xl flex items-start gap-4 relative z-10">
                <div className="w-10 h-10 bg-white rounded-xl shadow-sm flex items-center justify-center text-blue-500 shrink-0">
                    <ShieldCheck className="w-6 h-6" />
                </div>
                <p className="text-sm text-blue-800 leading-relaxed font-medium mt-0.5">
                    Your answers are strictly confidential and protected under health privacy laws. Only authorized medical staff can review this information.
                </p>
            </div>
        </div>
    );
};

export default Questionnaire;
