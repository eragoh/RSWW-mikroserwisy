export default {
    name: 'Reservations',
    components: {},
    data() {
      return {
        toursdata: [],
        tours: [],
      }
    },
    methods: {
      async load() {
        //const url = '/getmytours/'
        //this.tours = await (await fetch(url)).json();
        this.toursdata = [
          { name: '66329371bf2245d456ab3a2d', paid: false, price: 0},
          { name: '66329371bf2245d456ab3a2c', paid: true, price: 9.99},
          // Dodaj więcej elementów wycieczki według potrzeb
        ];
        for(const tour of this.toursdata){
            const url = '/tours/' + tour.name + '/get/'
            const response = await (await fetch(url)).json();
            this.tours.push({ response, paid: tour.paid, price: tour.price});
        }
      },
      redirectToReservation(url) {
        window.location.href = '/tours/' + url + '/buy/';
      },
      roomsf: function(t){
        var rooms = ''
        if(t.is_standard){
            rooms += '<span>Pokój standardowy</span>';
        }
        if(t.is_family){
            if(rooms !== ''){
                rooms += '<span class="text-primary"> • </span>';
            }
            rooms += '<span>Pokój rodzinny</span>';
        }
        if(t.is_apartment){
            if(rooms !== ''){
                rooms += '<span class="text-primary"> • </span>';
            }
            rooms += '<span>Apartament</span>';
        }
        if(t.is_studio){
            if(rooms !== ''){
                rooms += '<span class="text-primary"> • </span>';
            }
            rooms += '<span>Studio</span>';
        }
        return rooms;
      },        
    },
    computed: {},
    mounted() {
      this.load();
    },
    template: /*html*/`
    <div class="row justify-content-center mb-3" v-if="tours" v-for="tour in tours">
        <div class="col-md-12 col-xl-10">
            <div class="card shadow-0 border rounded-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-12 col-lg-3 col-xl-3 mb-4 mb-lg-0">
                            <div class="bg-image hover-zoom ripple rounded ripple-surface">
                            <a :href="tour.response._id.$oid"><img :src="tour.response.img" class="w-100" /></a>
                            </div>
                        </div>
                        <div class="col-md-6 col-lg-6 col-xl-6">
                            <h5>
                                <i class="bi bi-house"></i> 
                                <a :href="tour.response._id.$oid" style="text-decoration: none;">&nbsp{{tour.response.hotel}}</a>
                            </h5>
                            <div class="d-flex flex-row">
                                <div class="text-danger mb-1 me-2" v-for="star in tour.response.score">
                                    <i class="bi bi-star-fill"></i>                            
                                </div>
                                <div class="text-danger mb-1 me-2" v-for="star in 5 - tour.response.score">
                                    <i class="bi bi-star"></i>                            
                                </div>
                                <span>
                                    {{ tour.response.country }}{{ tour.response.city !== '' ? ', ' + tour.response.city : '' }}
                                </span>
                            </div>
                            <div class="mt-1 mb-0 text-muted small">
                                <i class="bi bi-calendar-range"></i> {{tour.response.start_date}} - {{tour.response.end_date}}<br />
                                <i class="bi bi-airplane"></i> {{tour.response.departure_location}}<br />
                                <div style="display: inline-flex; align-items: center;">
                                    <i class="bi bi-houses"></i>
                                    <div style="margin-left: 8px;" class="mb-2 text-muted small" v-html="roomsf(tour.response.room)"></div>
                                </div>
                            </div>
                            <p class="text-truncate mb-4 mb-md-0">
                                {{tour.response.description}}
                            </p>
                        </div>
                        <div class="col-md-6 col-lg-3 col-xl-3 border-sm-start-none border-start">
                            <div v-if="tour.paid">
                                <div class="d-flex flex-row align-items-center mb-1">
                                    <h4 class="mb-1 me-1">{{tour.price}}zł.</h4>
                                    <span class="text-danger"><s>{{Math.round(1.2 * tour.price) + 0.99}}zł</s></span>
                                </div>
                                <h6 class="text-success"><i class="bi bi-check"></i> Zakup opłacony</h6>
                            </div>
                            <div v-else>
                                <h6 class="text-danger"><i class="bi bi-x"></i> Zakup nieopłacony</h6>
                                <div class="d-flex flex-column mt-4">                                    
                                    <button @click="redirectToReservation(tour.response._id.$oid)" data-mdb-button-init data-mdb-ripple-init class="btn btn-outline-primary btn-sm mt-2" type="button">
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
    <div v-else>
        😔 Brak dostępnych wycieczek o podanych parametrach. 😔
    </div>
    `
  }
  