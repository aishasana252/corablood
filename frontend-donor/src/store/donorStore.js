import { create } from 'zustand';
import axios from 'axios';

export const useDonorStore = create((set) => ({
    donor: null,
    workflowId: null,
    currentStep: 'registration',
    steps: [],
    loading: true,
    error: null,

    fetchState: async () => {
        set({ loading: true });
        try {
            const response = await axios.get('/portal/api/state/');
            if (response.data.success) {
                const { donor, workflow_id, current_step, steps } = response.data.data;
                set({ 
                    donor, 
                    workflowId: workflow_id, 
                    currentStep: current_step, 
                    steps, 
                    loading: false 
                });
            } else {
                set({ error: response.data.message, loading: false });
            }
        } catch (err) {
            set({ error: "Failed to connect to donor system.", loading: false });
        }
    },

    setStep: (step) => set({ currentStep: step })
}));
