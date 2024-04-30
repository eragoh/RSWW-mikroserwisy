import Reservation from './reservation.js'
const {createApp} = Vue;
const app = createApp({
    components: {
        Reservation,
    }
});
app.mount('#app');