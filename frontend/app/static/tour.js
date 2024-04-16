export default{
    name: 'Tour',
    components: {},
    data() {
    return {
        tour: null
    }
},
    methods: {
        load: async function(){
            const url = window.location.href + '/get/';
            this.tour = await (await fetch(url)).json();
        },
        
    },
    computed: {},
    mounted() {
        this.load();
    },
    template: /*html*/`
    
    <div v-if="tour">
    <div class="my-3 p-3">
      <h2 class="display-5">{{ tour.city }}, {{ tour.country }}</h2>
      <img :src="tour.img" alt="Hotel Image" style="max-width: 100%;">
      <p class="lead">{{ tour.description }}</p>
    </div>
    <div>
      <h3>{{ tour.hotel }}</h3>
      <div class="d-flex flex-row">
      <div class="text-danger mb-1 me-2" v-for="star in tour.score">
            <i class="bi bi-star-fill"></i>                            
        </div>
        <div class="text-danger mb-1 me-2" v-for="star in 5 - tour.score">
            <i class="bi bi-star"></i>                            
        </div>
        </div>
      <div class="mt-1 mb-0 text-muted small">
        <span v-if="tour.room.is_standard">Pokój standardowy</span>
        <span v-if="tour.room.is_standard" class="text-primary"> • </span>
        <span v-if="tour.room.is_family">Pokój rodzinny</span>
        <span><br /></span>
        </div>
        <div class="mb-2 text-muted small">
        <span v-if="tour.room.is_apartment">Apartament</span>
        <span v-if="tour.room.is_apartment" class="text-primary"> • </span>
        <span v-if="tour.room.is_studio">Studio</span>
        <span><br /></span>
      </div>
    </div>
  </div>
  <div v-else>
    <p>Loading...</p>
  </div>

  `
}