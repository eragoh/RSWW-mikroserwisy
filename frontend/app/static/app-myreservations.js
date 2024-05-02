import Reservations from './myreservations.js'
const {createApp} = Vue;
const app = createApp({
    components: {
        Reservations,
    }
});
app.mount('#app');