import Tours from './tours.js'
const {createApp} = Vue;
const app = createApp({
    components: {
        Tours,
    }
});
app.mount('#app');