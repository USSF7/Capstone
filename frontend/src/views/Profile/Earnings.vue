<!-- Details on a user's overall earnings -->
<script lang="js" setup>

import { ref, onMounted, computed } from 'vue'
import { FwbTable, FwbTableBody, FwbTableCell, FwbTableHead, FwbTableHeadCell, FwbTableRow, FwbListGroup, FwbListGroupItem, FwbSpinner } from 'flowbite-vue'
import { Line } from "vue-chartjs"
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement, TimeScale, plugins } from "chart.js"
import { useAuthStore } from '../../stores/auth'
import RentalService from '../../services/rentalService'
import UserService from '../../services/userService'
import AuthService from '../../services/authService'
import 'chartjs-adapter-date-fns'

/**
 * Auth store providing current logged-in user.
 */
const auth = useAuthStore()

/** 
 * Whether the current user is a vendor 
 */
const isVendor = ref(false)

/** 
 * List of completed rentals for the vendor
 */
const vendorRentalsData = ref()

/**
 * Flag indicating whether initial data has loaded
 */
const vendorRentalsDataLoaded = ref(false)

/**
 * Cached list of all users
 */
const usersData = ref()

/**
 * Chart-ready dataset of individual rentals
 */
const chartDataRentals = ref([])

/**
 * Chart-ready dataset aggregated by month
 */
const chartDataRentalsByMonth = ref([])

/** 
 * Current authenticated user's ID
 */
const vendorId = computed(() => auth.user?.id)

/**
 * Validates whether the logged-in user has vendor permissions.
 * Sets isVendor based on auth store user data.
 */
async function validateVendorStatus() {
    // Determine if the user is a vendor
    if (auth.user?.vendor == true) {
        isVendor.value = true
    }
    else {
        isVendor.value = false
    }
}

/**
 * Loads completed rentals for the vendor and prepares raw rental list, chart dataset (per rental and monthly aggregated earnings), and user lookup data.
 * Handles sorting and transformation of rental earnings over time.
 */
async function loadCompletedVendorRentals() {
    try {
        // Getting the vendor's completed rentals data
        vendorRentalsData.value = await RentalService.getRentalsByVendorAndStatus(vendorId.value, 'returned')
        vendorRentalsData.value = vendorRentalsData.value.sort((a, b) => new Date(b.end_date) - new Date(a.end_date))

        // Putting some of the vendor's completed rentals data into chartDataRentals
        chartDataRentals.value = vendorRentalsData.value.map(rental => ({
            x: new Date(rental.end_date),
            y: rental.agreed_price
        }))
        .sort((a, b) => a.x - b.x)

        // Sorting the completed rentals data into months (using 0-indexed months to match Date.getMonth())
        let currentDate = new Date()
        let currentMonthYear = { Month: currentDate.getMonth(), Year: currentDate.getFullYear() }
        let pastMonthYear = { Month: currentDate.getMonth(), Year: currentDate.getFullYear() - 1 }

        while ((pastMonthYear.Month != currentMonthYear.Month) || (pastMonthYear.Year != currentMonthYear.Year)) {
            // Adding the earnings from the current month and year together
            let sumEarnings = 0.0
            for (let i = 0; i < chartDataRentals.value.length; i++) {
                if ((pastMonthYear.Month == chartDataRentals.value[i].x.getMonth()) &&
                    (pastMonthYear.Year  == chartDataRentals.value[i].x.getFullYear())) {
                    sumEarnings += chartDataRentals.value[i].y
                }
            }

            // Adding the month's earnings to chartDataRentalsByMonth
            chartDataRentalsByMonth.value.push({ x: new Date(pastMonthYear.Year, pastMonthYear.Month), y: sumEarnings })

            // Incrementing pastMonthYear
            pastMonthYear.Month += 1

            if (pastMonthYear.Month > 11) {
                pastMonthYear.Month = 0
                pastMonthYear.Year += 1
            }
        }

        // Getting all of the users in the database
        usersData.value = await UserService.getUsers()
    }
    catch (error) {
        console.error("Error getting vendor's rental data:", error)

        // Alerting the user that the user's data could not be loaded
        alert("Error: Rental data could not be loaded.")
    }
}

/**
 * Runs on component mount.
 * Validates vendor status.
 * Loads rental data if user is a vendor.
 * Marks page as ready for rendering.
 */
onMounted(async () => {
    // Validating the user's vendor status
    await validateVendorStatus()

    // Loading in the vendor's rental data
    if (isVendor.value == true) {
        await loadCompletedVendorRentals()
    }

    // Displaying the page to the user
    vendorRentalsDataLoaded.value = true
})

/**
 * Computes total earnings from all completed rentals.
 * @returns {number} Total revenue earned.
 */
function computeTotalEarnings() {
    let sum = 0.0
    if (vendorRentalsData.value != undefined) {
        for (let i = 0; i < vendorRentalsData.value.length; i++) {
            sum += vendorRentalsData.value[i].agreed_price
        }
    }

    return sum
}

/**
 * Computes total number of completed rentals.
 * @returns {number} Count of rentals.
 */
function computeNumberOfCompletedRentals() {
    let numOfCompletedRentals = 0
    if (vendorRentalsData.value != undefined) {
        numOfCompletedRentals = vendorRentalsData.value.length
    }

    return numOfCompletedRentals
}

/**
 * Retrieves a user's name from cached user data.
 * @param {number} userId - ID of the user.
 * @returns {string} User's name.
 */
function getUserName(userId) {
    let userName = ""
    if (usersData.value != undefined) {
        userName = usersData.value[userId - 1].name
    }

    return userName
}

/**
 * Formats a timestamp into a readable US locale date-time string.
 * @param {string|Date} value - Date value to format.
 * @returns {string} Formatted date string.
 */
function formatDateTime(value) {
    return new Date(value).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    })
}

// Setting up the monthly earnings line graph
ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement, TimeScale)

const chartData = computed(() => ({
  datasets: [
    {
      label: 'Earnings',
      data: chartDataRentalsByMonth.value,
      borderColor: 'green',
      backgroundColor: 'rgba(0,128,0,0.2)',
      tension: 0
    }
  ]
}))

const chartOptions = {
  scales: {
    x: {
        type: 'time',
        title: {
            display: true,
            text: 'Date'
        }
    },
    y: {
        title: {
          display: true,
          text: 'Money (USD)'
        },
        ticks: {
          callback: (value) => '$' + value.toFixed(2)
        }
    }
  },
  plugins: {
    tooltip: {
        callbacks: {
            title: function(context) {
                const date = new Date(context[0].parsed.x)
                return date.toLocaleDateString('en-US', {
                    month: 'long',
                    year: 'numeric'
                })
            },
            label: function(context) {
                return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`
            }
        }
    }
  }
}

</script>

<template>
    <div v-if="vendorRentalsDataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <div v-if="isVendor == false">
            <h1 class="text-3xl font-bold text-gray-800 mb-6">User does not have access to this page</h1>
        </div>
        <div v-else>
            <div class="space-y-4">
                <h1 class="text-3xl font-bold text-gray-800 mb-6">My Earnings</h1>
                <Line :data="chartData" :options="chartOptions" :height="100" aria-label="Line chart showing monthly rental earnings over the last 12 months in US dollars."/>
                <div class="grid grid-cols-2 gap-4">
                    <fwb-list-group class="w-full">
                        <fwb-list-group-item><b>Total Earnings</b>: ${{ computeTotalEarnings().toFixed(2) }}</fwb-list-group-item>
                    </fwb-list-group>
                    <fwb-list-group class="w-full">
                        <fwb-list-group-item><b>Number of Completed Rentals</b>: {{ computeNumberOfCompletedRentals() }}</fwb-list-group-item>
                    </fwb-list-group>
                </div>
                <fwb-table striped>
                    <fwb-table-head>
                        <fwb-table-head-cell>Renter</fwb-table-head-cell>
                        <fwb-table-head-cell>Location</fwb-table-head-cell>
                        <fwb-table-head-cell>Earnings</fwb-table-head-cell>
                        <fwb-table-head-cell>Start Date</fwb-table-head-cell>
                        <fwb-table-head-cell>End Date</fwb-table-head-cell>
                    </fwb-table-head>
                    <fwb-table-body>
                        <fwb-table-row v-for="rental in vendorRentalsData" :key="rental.id">
                            <fwb-table-cell>{{ getUserName(Number(rental.renter_id)) }}</fwb-table-cell>
                            <fwb-table-cell>{{ rental.location }}</fwb-table-cell>
                            <fwb-table-cell>${{ rental.agreed_price.toFixed(2) }}</fwb-table-cell>
                            <fwb-table-cell>{{ formatDateTime(rental.start_date) }}</fwb-table-cell>
                            <fwb-table-cell>{{ formatDateTime(rental.end_date) }}</fwb-table-cell>
                        </fwb-table-row>
                    </fwb-table-body>
                </fwb-table>
            </div>
        </div>
    </div>
</template>

<style scoped>

</style>