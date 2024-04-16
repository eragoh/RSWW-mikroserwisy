export default{
    name: 'Tours',
    props: ['description', 'page'],
    components: {},
    data() {
    return {
        tours: [],
        filter: '',
    }
},
    methods: {
        load: async function(){
            const url = '/gettoursss?page=' + this.page;
            this.tours = await (await fetch(url)).json();
        },
        redirectToTour(url) {
            window.location.href = url;
        }      
        
    },
    computed: {},
    mounted() {
        this.load();
    },
    template: /*html*/`
        <h3 class="text-center mt-3">{{description}}</h3>

        <section style="background-color: #eee;">
        <div class="container py-5">

            <div class="row justify-content-center mb-3" v-for="tour in tours">
            <div class="col-md-12 col-xl-10">
                <div class="card shadow-0 border rounded-3">
                <div class="card-body">
                    <div class="row">
                    <div class="col-md-12 col-lg-3 col-xl-3 mb-4 mb-lg-0">
                        <div class="bg-image hover-zoom ripple rounded ripple-surface">
                        <a :href="tour._id.$oid"><img :src="tour.img" class="w-100" /></a>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-6 col-xl-6">
                        <h5>
                            <i class="bi bi-house"></i> 
                            <a :href="tour._id.$oid" style="text-decoration: none;">&nbsp{{tour.hotel}}</a>
                        </h5>
                        <div class="d-flex flex-row">
                        <div class="text-danger mb-1 me-2" v-for="star in tour.score">
                            <i class="bi bi-star-fill"></i>                            
                        </div>
                        <div class="text-danger mb-1 me-2" v-for="star in 5 - tour.score">
                            <i class="bi bi-star"></i>                            
                        </div>
                        <span>{{tour.country}}, {{tour.city}}</span>
                        </div>
                        <div class="mt-1 mb-0 text-muted small">
                        <i class="bi bi-calendar-range"></i> {{tour.start_date}} - {{tour.end_date}}<br />
                        <i class="bi bi-airplane"></i> {{tour.departure_location}}<br />
                        <i class="bi bi-houses"></i> 
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
                        <p class="text-truncate mb-4 mb-md-0">
                        {{tour.description}}
                        </p>
                    </div>
                    <div class="col-md-6 col-lg-3 col-xl-3 border-sm-start-none border-start">
                        <div class="d-flex flex-row align-items-center mb-1">
                        <h4 class="mb-1 me-1">{{tour.price}}zł/os.</h4>
                        <span class="text-danger"><s>{{1.2 * tour.price}}zł</s></span>
                        </div>
                        <h6 class="text-success">Dostępny</h6>
                        <div class="d-flex flex-column mt-4">
                        
                        <button @click="redirectToTour(tour._id.$oid)" data-mdb-button-init data-mdb-ripple-init class="btn btn-primary btn-sm" type="button">Dalej</button>
                        <button data-mdb-button-init data-mdb-ripple-init class="btn btn-outline-primary btn-sm mt-2" type="button">
                            Kup teraz!
                        </button>
                        </div>
                    </div>
                    </div>
                </div>
                </div>
            </div>
            </div>


        </div>
        </section>

    `
}