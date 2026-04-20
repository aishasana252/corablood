import { create } from 'zustand'
import axios from 'axios'

// Helper to get CSRF token from cookies
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Global Axios Config
axios.defaults.headers.common['X-CSRFToken'] = getCookie('csrftoken');

export const useWorkflowStore = create((set, get) => ({
    donationId: window.WORKFLOW_ID || null,
    currentStep: window.INITIAL_STEP || null,
    tabs: [],
    donor: window.INITIAL_DONOR || null,
    loading: false,
    error: null,

    fetchState: async () => {
        const id = get().donationId;
        if (!id) return;

        set({ loading: true });
        try {
            const response = await axios.get(`/api/v2/workflow/${id}/state/`);
            if (response.data.success) {
                const { currentStep, tabs, donor } = response.data.data;
                set({ currentStep, tabs, donor, error: null });
            }
        } catch (err) {
            set({ error: "Failed to load workflow state" });
        } finally {
            set({ loading: false });
        }
    },

    setStep: (stepSlug) => set({ currentStep: stepSlug })
}))
