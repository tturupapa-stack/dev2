import axios from 'axios';

const url = 'https://api.data.go.kr/openapi/tn_pubr_public_health_functional_food_nutrition_info_api';

async function check() {
    try {
        const response = await axios.get(url, {
            maxRedirects: 0,
            validateStatus: status => status >= 200 && status < 400
        });
        console.log('Status:', response.status);
        console.log('Headers:', response.headers);
    } catch (error) {
        console.log('Error:', error.message);
        if (error.response) {
            console.log('Response Status:', error.response.status);
            console.log('Response Headers:', error.response.headers);
        }
    }
}

check();
