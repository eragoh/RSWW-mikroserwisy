import freservation from './freservation.js'
const {createApp} = Vue;
const app = createApp({
    components: {
        freservation,
    }
});
app.mount('#app');