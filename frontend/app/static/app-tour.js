import Tour from './tour.js'
const {createApp} = Vue;
const app = createApp({
    components: {
        Tour,
    }
});
app.mount('#app');